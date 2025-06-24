To download a test:

`python aops_downloader.py {year} {contest (8,10A,10B,12A,12B)} --output {name}.json`

The JSON output is a list of objects with keys `ID`, `Year`, `ProblemNumber`,
`QuestionType`, `Question`, `Answer` and `Solution`.

To render a test into HTML format:

`python renderer.py json {file.json} {output_dir}`
