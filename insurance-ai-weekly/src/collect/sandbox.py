from src.collect.official_insurer import collect_from_source

def collect_sandbox(source: dict, start_date, end_date, min_article_length: int = 80):
    return collect_from_source(source, start_date, end_date, min_article_length=min_article_length)
