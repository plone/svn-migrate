import setuptools

version = '0.1'

setuptools.setup(
    name='svn-migrate',
    version=version,
    description="svn2git command wrapper",
    long_description="",
    classifiers=[],
    keywords='plone git svn svn2git',
    author='Rok Garbas',
    author_email='rok@garbas.si',
    url='https://github.com/plone/svn-migrate',
    license='BSD',
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'argh',
        'requests',
        ],
    entry_points="""
        [console_scripts]
        svn-migrate = svnmigrate:main
        """,
    )
