from collections import defaultdict

def select_main_and_extra(articles, main_count: int, extra_count: int, caps: dict):
    sorted_articles = sorted(articles, key=lambda x: x.score, reverse=True)
    main = []
    extra = []
    by_company = defaultdict(int)
    global_count = 0

    for a in sorted_articles:
        if len(main) >= main_count:
            break
        if by_company[a.company] >= caps.get("max_same_company_main", 3):
            continue
        if a.country != "KR" and global_count >= caps.get("max_global_main", 3):
            continue
        main.append(a)
        a.selected_main = True
        by_company[a.company] += 1
        if a.country != "KR":
            global_count += 1

    used = {a.url for a in main}
    for a in sorted_articles:
        if a.url in used:
            continue
        if len(extra) >= extra_count:
            break
        extra.append(a)
    return main, extra
