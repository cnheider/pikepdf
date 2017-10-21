import pytest
from pikepdf import _qpdf as qpdf

import os
import platform
import shutil
from contextlib import suppress


def test_split_pdf(resources, outdir):
    q = qpdf.PDF.open(resources / "fourpages.pdf")

    for n, page in enumerate(q.pages):
        outpdf = qpdf.PDF.new()
        outpdf.pages.append(page)
        outpdf.save(outdir / "page{}.pdf".format(n + 1))

    assert len([f for f in outdir.iterdir() if f.name.startswith('page')]) == 4


def test_empty_pdf(outdir):
    q = qpdf.PDF.new()
    with pytest.raises(IndexError):
        q.pages[0]
    q.save(outdir / 'empty.pdf')


def test_replace_page(resources):
    q = qpdf.PDF.open(resources / "fourpages.pdf")
    q2 = qpdf.PDF.open(resources / "graph.pdf")

    assert len(q.pages) == 4
    q.pages[1] = q2.pages[0]
    assert len(q.pages) == 4
    assert q.pages[1].Resources.XObject.keys() == \
        q2.pages[0].Resources.XObject.keys()


def test_reverse_pages(resources, outdir):
    q = qpdf.PDF.open(resources / "fourpages.pdf")
    qr = qpdf.PDF.open(resources / "fourpages.pdf")

    lengths = [int(page.Contents.stream_dict.Length) for page in q.pages]

    qr.pages.reverse()
    qr.save(outdir / "reversed.pdf")

    for n, length in enumerate(lengths):
        assert q.pages[n].Contents.stream_dict.Length == length

    for n, length in enumerate(reversed(lengths)):
        assert qr.pages[n].Contents.stream_dict.Length == length


def test_evil_page_deletion(resources, outdir):
    from shutil import copy
    copy(resources / 'sandwich.pdf', outdir / 'sandwich.pdf')
    src = qpdf.PDF.open(outdir / 'sandwich.pdf')
    pdf = qpdf.PDF.open(resources / 'graph.pdf')

    pdf.pages.append(src.pages[0])

    del src.pages[0]    
    (outdir / 'sandwich.pdf').unlink()
    pdf.save(outdir / 'out.pdf')

    del pdf.pages[0]
    pdf.save(outdir / 'out2.pdf')

    del pdf.pages[0]
    pdf.save(outdir / 'out_nopages.pdf')


def test_append_all(resources, outdir):
    pdf = qpdf.PDF.open(resources / 'sandwich.pdf')
    pdf2 = qpdf.PDF.open(resources / 'fourpages.pdf')

    for page in pdf2.pages:
        pdf.pages.append(page)

    assert len(pdf.pages) == 5
    pdf.save(outdir / 'out.pdf')


def test_extend(resources, outdir):
    pdf = qpdf.PDF.open(resources / 'sandwich.pdf')
    pdf2 = qpdf.PDF.open(resources / 'fourpages.pdf')
    pdf.pages.extend(pdf2.pages)

    assert len(pdf.pages) == 5
    pdf.save(outdir / 'out.pdf')

