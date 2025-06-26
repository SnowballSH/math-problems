To download a single contest:

```
python aops_downloader.py {year} {contest} --output {name}.json
```

`{contest}` may be an AMC contest (e.g. `8`, `10A`, `12B`), an AIME contest
(e.g. `AIME I`, `AIME II`, or `AIME` for years prior to 2000), or `AHSME`.

The JSON output is a list of objects with keys `ID`, `Year`, `ProblemNumber`,
`QuestionType`, `Question`, `Answer` and `Solution`.

To render a test into HTML format:

```
python renderer.py json {file.json} {output_dir}
```

To download many contests automatically run:

```
python automated.py
```

Results are saved under `amc_problems/`, `aime_problems/`, and
`ahsme_problems/` depending on contest type.
