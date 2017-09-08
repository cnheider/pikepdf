import pytest
from pikepdf import _qpdf as qpdf, parse_content_stream
import os
from subprocess import run, PIPE


class PrintParser(qpdf.StreamParser):
    def __init__(self):
        super().__init__()

    def handle_object(self, obj):
        print(repr(obj))

    def handle_eof(self):
        print("--EOF--")


class ExceptionParser(qpdf.StreamParser):
    def __init__(self):
        super().__init__()

    def handle_object(self, obj):
        raise ValueError("I take exception to this")

    def handle_eof(self):
        print("--EOF--")


def test_open_pdf(resources):
    pdf = qpdf.Pdf.open(resources / 'graph.pdf')
    stream = pdf.pages[0]['/Contents']
    qpdf.Object.parse_stream(stream, PrintParser())


def test_parser_exception(resources):
    pdf = qpdf.Pdf.open(resources / 'graph.pdf')
    stream = pdf.pages[0]['/Contents']
    with pytest.raises(ValueError):
        qpdf.Object.parse_stream(stream, ExceptionParser())


def test_text_filter(resources, outdir):
    input_pdf = resources / 'veraPDF test suite 6-2-10-t02-pass-a.pdf'


    # Ensure the test PDF has detect we can find
    proc = run(['pdftotext', str(input_pdf), '-'],
        check=True, stdout=PIPE, encoding='utf-8')
    assert proc.stdout.strip() != '', "Need input test file that contains text"


    pdf = qpdf.Pdf.open(input_pdf)
    stream = pdf.pages[0].Contents

    keep = []
    for operands, command in parse_content_stream(stream):
        if command == qpdf.Object.Operator('Tj'):
            print("skipping Tj")
            continue
        keep.append((operands, command))

    new_stream = qpdf.Object.Stream(pdf, keep)
    print(new_stream.read_stream_data())
    pdf.pages[0]['/Contents'] = new_stream
    pdf.pages[0]['/Rotate'] = 90

    pdf.save(outdir / 'notext.pdf', True)

    proc = run(['pdftotext', str(outdir / 'notext.pdf'), '-'],
        check=True, stdout=PIPE, encoding='utf-8')

    assert proc.stdout.strip() == '', "Expected text to be removed"


def test_invalid_stream_object():
    with pytest.raises(TypeError):
        parse_content_stream(qpdf.Object.Dictionary({"/Hi": 3}))