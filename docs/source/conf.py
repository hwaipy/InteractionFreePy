# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import pathlib
import sys
from sphinx.builders.html import StandaloneHTMLBuilder
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'InteractionFreePy'
copyright = '2025, Hwaipy'
author = 'Hwaipy'

release = '0.1'
version = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    # 'autoapi.extension',
    'myst_parser',
    'sphinx_copybutton',
]
autosummary_generate = True  # Turn on sphinx.ext.autosummary
autoapi_dirs = ['../../interactionfreepy']

StandaloneHTMLBuilder.supported_image_types = [
    'image/svg+xml',
    'image/png',
    'image/jpeg'
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

locale_dirs = ['locale/']
gettext_compact = False

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

add_module_names = False

def dealBrokerParameter(app, what, name, obj, options, signature, return_annotation):
    # print(app, what, name, obj, options, signature, return_annotation)
    # if what in ("method", "function") and signature:
    #     # 将签名字符串拆分为参数列表
    #     params = list(signature.split("(")[1].split(")")[0].split(", "))
    #     if params and params[0] == "self":
    #         # 移除第一个参数（self）
    #         new_params = params[1:]
    #         # 重新构建签名字符串
    #         new_signature = f"({', '.join(new_params)})"
    #         return (new_signature, return_annotation)
    return (signature, return_annotation)

def setup(app):
    app.connect("autodoc-process-signature", dealBrokerParameter)