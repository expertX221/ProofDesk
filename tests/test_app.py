import json
import io
import importlib.util
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch
import app


class ReviewTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('reportlab'), 'PDF support not installed')
    def test_pdf_export_is_parseable_and_preserves_report(self):
        from pdf_report import create_report_pdf
        from pypdf import PdfReader
        data = {'mode': 'live', 'summary': 'A & B <review>', 'checks': [{'requirement': 'Include a license', 'status': 'missing', 'reason': 'Absent from evidence.', 'action': 'Add a license.', 'evidence_ids': []}]}
        pdf = create_report_pdf(data)
        self.assertTrue(pdf.startswith(b'%PDF-'))
        text = ''.join(p.extract_text() for p in PdfReader(io.BytesIO(pdf)).pages)
        self.assertIn('A & B <review>', text)
        self.assertIn('Include a license', text)
        self.assertIn('Add a license.', text)

    def test_malformed_citations_do_not_crash(self):
        for ids in (None, 'repo', 42, {'repo': True}):
            report = app.validate_report({'checks': [{'status': 'verified', 'evidence_ids': ids}]}, [{'id': 'repo'}])
            self.assertEqual(report['checks'][0]['status'], 'needs_review')

    def test_unverified_notes_cannot_verify_a_requirement(self):
        report = app.validate_report({'checks': [{'status': 'verified', 'evidence_ids': ['notes', 'notes']}]}, [{'id': 'notes'}])
        self.assertEqual(report['checks'][0]['status'], 'needs_review')
        self.assertEqual(report['checks'][0]['evidence_ids'], ['notes'])

    def test_vercel_https_origin(self):
        handler = app.Handler.__new__(app.Handler)
        handler.path = '/api/analyze'
        handler.headers = {'Origin': 'https://proofdesk.vercel.app', 'Host': 'proofdesk.vercel.app', 'Content-Length': '2'}
        handler.rfile = io.BytesIO(b'{}')
        with patch.dict(app.os.environ, {'VERCEL': '1'}), patch.object(app, 'analyze', return_value={'mode': 'live'}), patch.object(handler, 'send') as send:
            handler.do_POST()
            send.assert_called_once_with(200, {'mode': 'live'})

    def test_unfounded_verification_downgraded(self):
        report = app.validate_report({'checks': [{'requirement': 'License', 'status': 'verified', 'evidence_ids': ['invented']}]}, [{'id': 'repo'}])
        self.assertEqual(report['checks'][0]['status'], 'needs_review')
        self.assertEqual(report['checks'][0]['evidence_ids'], [])

    def test_repository_host_validation(self):
        for url in ['http://github.com/a/b', 'https://github.com.evil.test/a/b', 'https://localhost/a/b', 'https://github.com/a/b/tree/main']:
            with self.assertRaises(ValueError):
                app.repository_evidence(url)

    def test_live_integration_with_mocked_services(self):
        evidence = [{'id': 'repo', 'text': 'MIT', 'path': 'metadata', 'url': 'https://github.com/a/b'}]
        completion = {'choices': [{'message': {'content': json.dumps({'checks': [{'requirement': 'license', 'status': 'verified', 'evidence_ids': ['repo']}]})}}], 'usage': {'total_tokens': 42}}
        with patch.dict(app.os.environ, {'NEBIUS_API_KEY': 'test-key'}), patch.object(app, 'repository_evidence', return_value=(evidence, {'files_read': 0})), patch.object(app, 'fetch_json', return_value=completion) as call:
            report = app.analyze({'requirements': 'MIT license', 'repository': 'https://github.com/a/b'})
            self.assertEqual(report['mode'], 'live')
            self.assertEqual(report['checks'][0]['status'], 'verified')
            self.assertIn('/chat/completions', call.call_args.args[0])

    def test_http_assets_sample_and_origin(self):
        server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            for path in ['/', '/app.js', '/style.css', '/api/config', '/api/sample']:
                with urllib.request.urlopen(base + path) as response:
                    self.assertEqual(response.status, 200)
                    self.assertGreater(len(response.read()), 20)
            request = urllib.request.Request(base + '/api/analyze', data=b'{}', headers={'Origin': 'https://evil.test', 'Content-Type': 'application/json'})
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request)
            self.assertEqual(error.exception.code, 403)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()
