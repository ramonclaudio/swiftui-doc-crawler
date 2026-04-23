# swiftui-doc-crawler

When I started building SwiftUI-heavy apps, LLMs kept hallucinating API signatures. Apple's docs are JS-rendered and scattered across hundreds of endpoints, no clean way to feed them into a model as context. So I wrote this: crawl the Apple Developer site for SwiftUI docs, parse the endpoints, spit out Markdown I can paste into any LLM as grounding.

Python crawler for Apple Developer SwiftUI documentation. Outputs Markdown.

## Install

```bash
git clone https://github.com/ramonclaudio/swiftui-doc-crawler.git
cd swiftui-doc-crawler
pip install -r requirements.txt
```

## Usage

```python
import swiftui

# Crawl every SwiftUI endpoint
swiftui.crawl()

# Single page
swiftui.crawl('https://developer.apple.com/documentation/swiftui/app', mode='single')

# Collection (page + linked children)
swiftui.crawl('https://developer.apple.com/documentation/swiftui/app', mode='collection')
```

## Output

- `data/raw/endpoints.json`, raw crawl results
- `data/processed/processed_endpoints.json`, parsed structured docs
- Formatted Markdown via the `markdown_formatter` module

## License

MIT
