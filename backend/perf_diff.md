| Execution Part | Playwright Time (s) | HTTPX + Selectolax Time (s) | Faster Framework |
| :--- | :---: | :---: | :---: |
| **Setup** *(Make client/browser, launch, load)* | 0.574692 | 2.058192 | **Playwright** (by 1.4835s) |
| **Query: 'adobe'** *(Search, parse, extract, open page)* | 3.214527 | 2.013489 | **HTTPX + Selectolax** (by 1.2010s) |
| **Query: 'chrome'** *(Search, parse, extract, open page)* | 1.363011 | 1.012552 | **HTTPX + Selectolax** (by 0.3505s) |

| Metric (Overall Programmatic Summary) | Playwright | HTTPX + Selectolax | Better Performance |
| :--- | :---: | :---: | :---: |
| **Sum of Programmatic Steps (Time)** | 5.152230s | 5.084233s | **HTTPX + Selectolax** (by 0.0680s) |
| **Calculated Programmatic Runtime** | 6.539910s | 5.089641s | **HTTPX + Selectolax** (by 1.4503s) |
| **Peak RAM Usage** | 37.14 MB | 53.02 MB | **Playwright** (by 15.88 MB lower) |
| **RAM Delta** | +4.89 MB | +18.17 MB | **Playwright** (by 13.28 MB lower) |