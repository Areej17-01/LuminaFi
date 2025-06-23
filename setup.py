from setuptools import setup, find_packages

setup(
    name='luminafi',
    version='0.1.0',
    description='AI-powered financial analysis app with Streamlit',
    author='Areej',
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'yfinance',
        'pandas',
        'plotly',
        'matplotlib',
        'seaborn',
        'together',
        'websockets',
        'python-dotenv'
    ],
    include_package_data=True,
    python_requires='>=3.8',
) 