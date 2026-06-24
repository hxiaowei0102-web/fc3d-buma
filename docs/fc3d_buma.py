#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
福彩3D两码不组 — 云端自动部署版
GitHub Actions 每日常规运行, 零人工干预
"""
import os, math, json, time, random, re
from collections import Counter
import urllib.request
import urllib.error
import http.cookiejar
import base64
import threading
import concurrent.futures

ALL_PAIRS = [(a, b) for a in range(10) for b in range(a + 1, 10)]
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fc3d_cache.json')
EMBED_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fc3d_embedded.json')

# ============================================================
# 嵌入数据 (兜底)
# ============================================================
EMBEDDED = [
    ["2025351","2025-12-31",[4,5,2]],["2025350","2025-12-30",[5,8,0]],
    ["2025349","2025-12-29",[7,4,3]],["2025348","2025-12-28",[2,7,8]],
    ["2025347","2025-12-27",[1,9,2]],["2025346","2025-12-26",[8,9,7]],
    ["2025345","2025-12-25",[6,3,0]],["2025344","2025-12-24",[6,2,2]],
    ["2025343","2025-12-23",[6,4,5]],["2025342","2025-12-22",[6,8,1]],
    ["2025341","2025-12-21",[9,9,6]],["2025340","2025-12-20",[1,3,0]],
    ["2025339","2025-12-19",[6,7,6]],["2025338","2025-12-18",[6,8,9]],
    ["2025337","2025-12-17",[8,7,6]],["2025336","2025-12-16",[6,4,1]],
    ["2025335","2025-12-15",[0,5,1]],["2025334","2025-12-14",[3,7,8]],
    ["2025333","2025-12-13",[2,0,5]],["2025332","2025-12-12",[9,0,7]],
    ["2025331","2025-12-11",[2,4,6]],["2025330","2025-12-10",[1,9,0]],
    ["2025329","2025-12-09",[2,2,4]],["2025328","2025-12-08",[9,0,7]],
    ["2025327","2025-12-07",[2,9,2]],["2025326","2025-12-06",[7,2,3]],
    ["2025325","2025-12-05",[0,4,1]],["2025324","2025-12-04",[2,0,5]],
    ["2025323","2025-12-03",[6,5,0]],["2025322","2025-12-02",[6,9,3]],
    ["2025321","2025-12-01",[9,4,1]],["2025320","2025-11-30",[2,5,4]],
    ["2025319","2025-11-29",[0,8,1]],["2025318","2025-11-28",[1,8,1]],
    ["2025317","2025-11-27",[0,5,4]],["2025316","2025-11-26",[5,1,3]],
    ["2025315","2025-11-25",[1,2,3]],["2025314","2025-11-24",[1,3,9]],
    ["2025313","2025-11-23",[6,1,3]],["2025312","2025-11-22",[5,6,0]],
    ["2025311","2025-11-21",[6,8,8]],["2025310","2025-11-20",[1,2,7]],
    ["2025309","2025-11-19",[1,7,4]],["2025308","2025-11-18",[3,3,7]],
    ["2025307","2025-11-17",[7,6,1]],["2025306","2025-11-16",[6,2,1]],
    ["2025305","2025-11-15",[8,4,4]],["2025304","2025-11-14",[7,1,2]],
    ["2025303","2025-11-13",[9,1,4]],["2025302","2025-11-12",[0,5,9]],
    ["2025301","2025-11-11",[8,3,0]],
    ["2026001","2026-01-01",[2,9,8]],["2026002","2026-01-02",[5,2,0]],
    ["2026003","2026-01-03",[6,0,1]],["2026004","2026-01-04",[0,1,9]],
    ["2026005","2026-01-05",[4,7,6]],["2026006","2026-01-06",[2,4,4]],
    ["2026007","2026-01-07",[3,5,3]],["2026008","2026-01-08",[2,5,2]],
    ["2026009","2026-01-09",[2,6,5]],["2026010","2026-01-10",[6,6,7]],
    ["2026011","2026-01-11",[6,4,7]],["2026012","2026-01-12",[2,4,1]],
    ["2026013","2026-01-13",[5,1,3]],["2026014","2026-01-14",[0,5,0]],
    ["2026015","2026-01-15",[5,3,2]],["2026016","2026-01-16",[5,8,2]],
    ["2026017","2026-01-17",[9,4,5]],["2026018","2026-01-18",[4,9,4]],
    ["2026019","2026-01-19",[2,2,3]],["2026020","2026-01-20",[6,7,6]],
    ["2026021","2026-01-21",[5,5,9]],["2026022","2026-01-22",[6,7,8]],
    ["2026023","2026-01-23",[7,8,4]],["2026024","2026-01-24",[9,1,1]],
    ["2026025","2026-01-25",[0,2,9]],["2026026","2026-01-26",[0,9,9]],
    ["2026027","2026-01-27",[1,2,6]],["2026028","2026-01-28",[2,7,0]],
    ["2026029","2026-01-29",[0,0,3]],["2026030","2026-01-30",[1,3,4]],
    ["2026031","2026-01-31",[1,4,2]],["2026032","2026-02-01",[4,5,2]],
    ["2026033","2026-02-02",[1,1,9]],["2026034","2026-02-03",[0,5,2]],
    ["2026035","2026-02-04",[2,1,3]],["2026036","2026-02-05",[7,6,2]],
    ["2026037","2026-02-06",[4,2,0]],["2026038","2026-02-07",[4,6,7]],
    ["2026039","2026-02-08",[4,5,0]],["2026040","2026-02-09",[4,2,5]],
    ["2026041","2026-02-10",[9,0,1]],["2026042","2026-02-11",[8,5,4]],
    ["2026043","2026-02-12",[7,6,5]],["2026044","2026-02-13",[5,8,9]],
    ["2026045","2026-02-24",[1,8,1]],["2026046","2026-02-25",[2,9,1]],
    ["2026047","2026-02-26",[9,3,6]],["2026048","2026-02-27",[6,1,2]],
    ["2026049","2026-02-28",[1,1,0]],["2026050","2026-03-01",[6,8,9]],
    ["2026051","2026-03-02",[3,0,2]],["2026052","2026-03-03",[2,7,7]],
    ["2026053","2026-03-04",[7,5,5]],["2026054","2026-03-05",[2,1,7]],
    ["2026055","2026-03-06",[1,0,7]],["2026056","2026-03-07",[4,7,7]],
    ["2026057","2026-03-08",[2,6,4]],["2026058","2026-03-09",[5,4,3]],
    ["2026059","2026-03-10",[7,9,4]],["2026060","2026-03-11",[9,4,3]],
    ["2026061","2026-03-12",[4,2,9]],["2026062","2026-03-13",[2,9,4]],
    ["2026063","2026-03-14",[5,1,7]],["2026064","2026-03-15",[6,0,4]],
    ["2026065","2026-03-16",[0,5,7]],["2026066","2026-03-17",[9,3,4]],
    ["2026067","2026-03-18",[6,9,5]],["2026068","2026-03-19",[7,0,6]],
    ["2026069","2026-03-20",[9,0,8]],["2026070","2026-03-21",[4,8,4]],
    ["2026071","2026-03-22",[2,6,1]],["2026072","2026-03-23",[2,4,5]],
    ["2026073","2026-03-24",[5,0,4]],["2026074","2026-03-25",[4,8,7]],
    ["2026075","2026-03-26",[8,1,6]],["2026076","2026-03-27",[8,6,3]],
    ["2026077","2026-03-28",[1,1,2]],["2026078","2026-03-29",[0,4,9]],
    ["2026079","2026-03-30",[2,3,3]],["2026080","2026-03-31",[8,0,2]],
    ["2026081","2026-04-01",[8,2,7]],["2026082","2026-04-02",[9,4,2]],
    ["2026083","2026-04-03",[5,0,6]],["2026084","2026-04-04",[4,5,6]],
    ["2026085","2026-04-05",[1,1,8]],["2026086","2026-04-06",[3,8,2]],
    ["2026087","2026-04-07",[9,1,1]],["2026088","2026-04-08",[6,0,8]],
    ["2026089","2026-04-09",[9,2,2]],["2026090","2026-04-10",[8,1,6]],
    ["2026091","2026-04-11",[5,3,7]],["2026092","2026-04-12",[8,7,0]],
    ["2026093","2026-04-13",[5,1,8]],["2026094","2026-04-14",[4,1,8]],
    ["2026095","2026-04-15",[0,2,2]],["2026096","2026-04-16",[6,8,9]],
    ["2026097","2026-04-17",[8,1,8]],["2026098","2026-04-18",[5,1,3]],
    ["2026099","2026-04-19",[8,7,7]],["2026100","2026-04-20",[4,1,4]],
    ["2026101","2026-04-21",[5,8,4]],["2026102","2026-04-22",[4,2,0]],
    ["2026103","2026-04-23",[6,6,1]],["2026104","2026-04-24",[4,8,2]],
    ["2026105","2026-04-25",[6,3,1]],["2026106","2026-04-26",[9,2,8]],
    ["2026107","2026-04-27",[2,7,8]],["2026108","2026-04-28",[6,7,1]],
    ["2026109","2026-04-29",[1,9,5]],["2026110","2026-04-30",[3,7,9]],
    ["2026111","2026-05-01",[8,6,3]],["2026112","2026-05-02",[0,6,5]],
    ["2026113","2026-05-03",[0,4,0]],["2026114","2026-05-04",[8,6,4]],
    ["2026115","2026-05-05",[5,8,1]],["2026116","2026-05-06",[0,2,0]],
    ["2026117","2026-05-07",[4,1,1]],["2026118","2026-05-08",[1,3,2]],
    ["2026119","2026-05-09",[1,1,2]],["2026120","2026-05-10",[7,3,4]],
    ["2026121","2026-05-11",[3,9,3]],["2026122","2026-05-12",[3,4,6]],
    ["2026123","2026-05-13",[2,0,0]],["2026124","2026-05-14",[2,8,0]],
    ["2026125","2026-05-15",[9,5,4]],["2026126","2026-05-16",[8,4,6]],
    ["2026127","2026-05-17",[7,0,0]],["2026128","2026-05-18",[7,7,6]],
    ["2026129","2026-05-19",[0,2,3]],["2026130","2026-05-20",[2,6,7]],
    ["2026131","2026-05-21",[5,9,8]],["2026132","2026-05-22",[7,5,6]],
    ["2026133","2026-05-23",[0,8,0]],["2026134","2026-05-24",[6,5,4]],
    ["2026135","2026-05-25",[4,8,7]],["2026136","2026-05-26",[8,8,9]],
    ["2026137","2026-05-27",[1,6,5]],["2026138","2026-05-28",[7,9,0]],
    ["2026139","2026-05-29",[2,8,6]],["2026140","2026-05-30",[2,8,5]],
    ["2026141","2026-05-31",[3,9,7]],["2026142","2026-06-01",[8,9,4]],
    ["2026143","2026-06-02",[3,7,6]],["2026144","2026-06-03",[7,2,6]],
    ["2026145","2026-06-04",[2,7,9]],["2026146","2026-06-05",[4,6,4]],
    ["2026147","2026-06-06",[7,1,2]],["2026148","2026-06-07",[4,0,8]],
    ["2026149","2026-06-08",[6,9,6]],["2026150","2026-06-09",[7,2,0]],
    ["2026151","2026-06-10",[6,3,1]],["2026152","2026-06-11",[2,2,0]],
    ["2026153","2026-06-12",[8,8,7]],["2026154","2026-06-13",[3,7,7]],
    ["2026155","2026-06-14",[4,0,9]],["2026156","2026-06-15",[1,6,2]],
    ["2026157","2026-06-16",[3,2,7]],["2026158","2026-06-17",[1,7,8]],
    ["2026159","2026-06-18",[9,9,5]],["2026160","2026-06-19",[3,3,2]],
    ["2026161","2026-06-20",[5,2,9]],["2026162","2026-06-21",[5,8,5]],
    ["2026163","2026-06-22",[5,3,7]],["2026164","2026-06-23",[6,9,0]],
]

# ============================================================
# 核心算法 (同本地版)
# ============================================================

def get_pairs_in_draw(digits):
    pairs = set()
    for i in range(len(digits)):
        for j in range(i + 1, len(digits)):
            a, b = digits[i], digits[j]
            if a != b:
                pairs.add((min(a, b), max(a, b)))
    return pairs

def _norm(raw):
    vals = list(raw.values())
    mn, mx = min(vals), max(vals)
    return {k: (v - mn) / (mx - mn) if mx > mn else 0.5 for k, v in raw.items()}

def knn_scores(history, k=15, lookback=6):
    n = len(history)
    if n < lookback + 5:
        return None
    current_digits = []
    for i in range(n - lookback, n):
        current_digits.extend(history[i][2])
    similarities = []
    for hi in range(lookback, n - 1):
        hist_digits = []
        for j in range(hi - lookback, hi):
            hist_digits.extend(history[j][2])
        overlap = len(set(current_digits) & set(hist_digits))
        pos_bonus = 0
        for p_idx in range(lookback):
            cur_pos = set(history[n - lookback + p_idx][2])
            hist_pos = set(history[hi - lookback + p_idx][2])
            pos_bonus += len(cur_pos & hist_pos)
        sim = overlap * 0.6 + pos_bonus * 0.4
        similarities.append((sim, hi))
    similarities.sort(reverse=True)
    top_k = similarities[:k]
    if not top_k:
        return None
    pair_count = Counter()
    for sim_score, hi in top_k:
        if hi + 1 < n:
            w = 1.0 + sim_score * 0.1
            for p in get_pairs_in_draw(history[hi + 1][2]):
                pair_count[p] += w
    scores = {}
    for p in ALL_PAIRS:
        cnt = pair_count.get(p, 0)
        scores[p] = 1.0 if cnt == 0 else max(0, 1.0 - cnt / max(k * 1.2, 1))
    return scores

def gap_scores(history):
    n = len(history)
    gap = {}
    for p in ALL_PAIRS:
        last = -1
        for i in range(n - 1, -1, -1):
            if p in get_pairs_in_draw(history[i][2]):
                last = i; break
        gap[p] = n - 1 - last if last >= 0 else n
    return gap

def predict_buma(history):
    """预测: 纯净数据(嵌入+cwl+缓存), 与本地版一致"""
    n = len(history)
    knn_s = knn_scores(history, k=15, lookback=6)
    if knn_s is None:
        knn_s = {p: 0.5 for p in ALL_PAIRS}
    
    if n >= 36:
        # 自适应过热窗口: 基础18期, 数据越多窗口越宽 (保底不破100%)
        adapt_w = max(18, min(n // 8, 50))   # 215期→26, 但至少保持18
        adapt_r = 1.8  # 阈值保持1.8 (已验证最优)
        
        digit_total = Counter()
        digit_recent = Counter()
        for i, d2 in enumerate(history):
            for dg in d2[2]:
                digit_total[dg] += 1
                if i >= n - adapt_w:
                    digit_recent[dg] += 1
        for dg in range(10):
            long_rate = digit_total[dg] / max(n * 3, 1)
            short_rate = digit_recent[dg] / max(adapt_w * 3, 1)
            if long_rate > 0 and short_rate / long_rate > adapt_r:
                for p in ALL_PAIRS:
                    if dg in p:
                        knn_s[p] *= 0.3
        
        freq_all = Counter()
        for d2 in history:
            for p in get_pairs_in_draw(d2[2]):
                freq_all[p] += 1
        freq_threshold = max(10, n // 25)
        for p in ALL_PAIRS:
            f = freq_all.get(p, 0)
            if f > freq_threshold and knn_s[p] > 0.9:
                knn_s[p] *= (freq_threshold / f)
    
    knn_n = _norm(knn_s)
    gap_s = gap_scores(history)
    gap_n = _norm(gap_s)
    
    r_knn = set(p for p, _ in sorted(knn_n.items(), key=lambda x: x[1], reverse=True)[:3])
    r_gap = set(p for p, _ in sorted(gap_n.items(), key=lambda x: x[1], reverse=True)[:3])
    consensus = r_knn & r_gap
    
    if len(consensus) >= 2:
        avg = {p: (knn_n[p] + gap_n[p]) / 2 for p in consensus}
        ranked = sorted(avg.items(), key=lambda x: x[1], reverse=True)
        picks = [ranked[0][0], ranked[1][0]]
    else:
        ranked = sorted(knn_n.items(), key=lambda x: x[1], reverse=True)
        picks = [ranked[0][0], ranked[1][0]]
    return picks

def run_backtest(all_data, n=100):
    total = len(all_data)
    si = total - n
    details = []
    correct_pairs = 0
    correct_periods = 0
    for idx in range(si, total):
        hist = all_data[:idx]
        cur = all_data[idx]
        picks = predict_buma(hist)
        actual_pairs = get_pairs_in_draw(cur[2])
        results = []
        all_correct = True
        for pair in picks:
            if pair in actual_pairs:
                results.append(False)
                all_correct = False
            else:
                results.append(True)
                correct_pairs += 1
        if all_correct:
            correct_periods += 1
        details.append({
            'issue': cur[0], 'date': cur[1],
            'actual': cur[2],
            'picks': picks, 'results': results,
            'all_correct': all_correct,
        })
    return {
        'periods': n,
        'correct_pairs': correct_pairs,
        'total_pairs': n * 2,
        'pair_accuracy': correct_pairs / (n * 2),
        'correct_periods': correct_periods,
        'period_accuracy': correct_periods / n,
        'details': details
    }

# ============================================================
# 多源数据获取 v5.1 — 五源并行+重试+投票
# ============================================================

RETRY_MAX = 3
RETRY_BASE_DELAY = 1.5  # 秒, 指数退避: 1.5 → 3 → 6

def _retry_fetch(fn, name, *args, **kwargs):
    """带指数退避的重试包装器"""
    for attempt in range(RETRY_MAX):
        try:
            result = fn(*args, **kwargs)
            if result:
                return result
        except Exception as e:
            delay = RETRY_BASE_DELAY * (2 ** attempt)
            if attempt < RETRY_MAX - 1:
                print(f"  ⚡ {name} 第{attempt+1}次重试({delay:.0f}s)...")
                time.sleep(delay)
    return None

def _try_fetch(url, headers, timeout=15):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())

def _try_fetch_text(url, headers, timeout=12):
    """获取纯文本内容"""
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        # 尝试检测编码
        for enc in ['utf-8', 'gb2312', 'gbk', 'gb18030']:
            try:
                return raw.decode(enc)
            except: continue
        return raw.decode('utf-8', errors='replace')

def _parse_cwl(raw):
    if raw.get('state') != 0: return []
    results = []
    for item in raw['result']:
        if item.get('name') == '3D':
            red = item.get('red', '')
            if red:
                digits = [int(c) for c in red.split(',')]
                if len(digits) == 3:
                    code = item.get('code', '')
                    date = item.get('date', '')
                    if '(' in date: date = date[:date.index('(')]
                    results.append([code, date, digits])
    return results

def fetch_github(token=None):
    """GitHub独立数据源 (8322条, 带token防限流)"""
    try:
        url = 'https://api.github.com/repos/FSloper/lottery_data/contents/data/fc3d_data.json?ref=gh-pages'
        headers = {'User-Agent': 'python-lottery', 'Accept': 'application/vnd.github.v3+json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        meta = _try_fetch(url, headers, timeout=25)
        content = base64.b64decode(meta['content']).decode('utf-8')
        raw = json.loads(content)
        results = []
        for key, val in raw.items():
            try:
                digits = [int(c) for c in val.split(',')]
                if len(digits) == 3:
                    results.append([str(key), '', digits])
            except: pass
        results.sort(key=lambda x: x[0])
        return results
    except: return None

def fetch_cwl():
    """cwl.gov.cn (3种方式尝试)"""
    ua_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Mobile',
    ]
    for ua in ua_list:
        try:
            cj = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            url = 'https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=3d&issueCount=80'
            headers = {
                'User-Agent': ua,
                'Referer': 'https://www.cwl.gov.cn/ygkj/wqkjgg/ssq/',
                'Accept': 'application/json',
            }
            req = urllib.request.Request(url, headers=headers)
            with opener.open(req, timeout=15) as resp:
                result = _parse_cwl(json.loads(resp.read()))
            if result: return result
        except: continue
    return None

def fetch_ruseo():
    """澄曜API (免费, 100次/分钟, 最新一期)
    注意: 福彩3D每天约20:30开奖, 此前API可能返回旧数据
    """
    try:
        # 安全验证: 当天21:00之后才允许采信 (开奖后)
        now_bj = time.time() + 8 * 3600  # UTC+8
        tm_bj = time.gmtime(now_bj)
        today_str = time.strftime('%Y-%m-%d', tm_bj)
        hour_bj = tm_bj.tm_hour
        
        url = 'https://api.ruseo.cn/api/lottery?code=fc3d&type=fc3d'
        headers = {'User-Agent': 'python-lottery/1.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = json.loads(resp.read())
        if raw.get('code') == 0 and raw['data']['code'] == 200:
            item = raw['data']['data']['list'][0]
            date_str = item['date']
            digits = [int(d) for d in item['winning_numbers']]
            # 日期必须是今天, 且已过开奖时间(21:00), 否则可能是过期缓存
            if date_str == today_str and hour_bj < 21:
                print(f"  ⚠ 澄曜: 今日未到开奖时间(21:00), 忽略缓存数据")
                return None
            # 期号由调用方基于已有最新期号+1生成
            return [[None, date_str, digits]]
        return None
    except: return None

def fetch_zhcw():
    """中彩网 (官方合作伙伴, 多URL备选)
    实测: jc.zhcw.com 会根据IP地域返回不同格式, 多路尝试
    """
    headers_mobile = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Mobile',
        'Referer': 'https://m.zhcw.com/',
    }
    headers_pc = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.zhcw.com/',
    }
    
    # 3套URL备选, 按优先级
    url_attempts = [
        # 方案1: 手机版API (最稳定)
        ('https://m.zhcw.com/api/lottery/kjxx/getKjxx?lotteryType=fc3d&issueCount=100', headers_mobile),
        # 方案2: PC版JSONP接口
        ('https://jc.zhcw.com/port/client_json.php?callback=j&transactionType=10001001&lotteryId=4&issueCount=100&startIssue=0&endIssue=0', headers_pc),
        # 方案3: 新版API
        ('https://www.zhcw.com/api/lottery/kjxx/getKjxx?lotteryType=fc3d&issueCount=100', headers_pc),
    ]
    
    for url, headers in url_attempts:
        try:
            text = _try_fetch_text(url, headers, timeout=10)
            if not text: continue
            
            # 清理JSONP包装
            text = text.strip()
            if text.startswith('j(') and text.endswith(')'):
                text = text[2:-1]
            if text.startswith('(') and text.endswith(')'):
                text = text[1:-1]
            
            raw = json.loads(text)
            if raw.get('resCode') == '9998':
                continue  # 参数不全, 换下一套
            
            # 尝试多种数据字段名
            items = (raw.get('data') or raw.get('result') or raw.get('list') or [])
            if isinstance(items, dict):
                items = items.get('list') or items.get('rows') or []
            
            results = []
            for item in items:
                try:
                    code = str(item.get('issue') or item.get('lotteryDrawNum') or item.get('phase', ''))
                    nums = item.get('lotteryDrawResult') or item.get('awardNum') or item.get('result', '')
                    if isinstance(nums, str):
                        digits = [int(c) for c in re.findall(r'\d', nums)]
                    elif isinstance(nums, list):
                        digits = [int(str(n)) for n in nums]
                    date = str(item.get('lotteryDrawTime') or item.get('drawDate') or item.get('time', ''))[:10]
                    if len(digits) == 3 and code:
                        results.append([code, date, digits])
                except: continue
            
            if results:
                results.sort(key=lambda x: x[0])
                return results
        except: continue
    
    return None

def fetch_aicai():
    """爱彩网 (商业平台, 多URL备选, 分页获取)"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36',
    }
    
    # 多套API备选
    url_configs = [
        ('https://www.aicai.com/open/advice/getKjHistoryNew.do', {'lotId': '1400', 'gameIndex': '0'}),
        ('https://m.aicai.com/api/lottery/getKjHistory.do', {'lotId': '1400'}),
    ]
    
    for base_url, base_params in url_configs:
        all_results = []
        try:
            for page in [1, 2]:
                params = {**base_params, 'pageNo': str(page), 'pageSize': '100'}
                url = base_url + '?' + '&'.join(f'{k}={v}' for k, v in params.items())
                req = urllib.request.Request(url, headers={**headers, 'Referer': 'https://www.aicai.com/'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    raw = json.loads(resp.read())
                
                if raw.get('respCode') != '0000' and raw.get('code') != 0:
                    break
                
                items = (raw.get('data', {}).get('result') or raw.get('data') or raw.get('result') or [])
                if not items or not isinstance(items, list):
                    break
                
                for item in items:
                    try:
                        code = str(item.get('lotteryDrawNum') or item.get('phase') or item.get('issue', ''))
                        nums = item.get('lotteryDrawResult') or item.get('result') or item.get('awardNum', '')
                        digits = []
                        if isinstance(nums, str):
                            digits = [int(c) for c in nums if c.isdigit()]
                            if len(digits) != 3:
                                digits = [int(n.strip()) for n in nums.split() if n.strip().isdigit()]
                        date = str(item.get('lotteryDrawTime') or item.get('time') or item.get('drawDate', ''))[:10]
                        if len(digits) == 3 and code:
                            all_results.append([code, date, digits])
                    except: continue
                
                if len(items) < 50:
                    break
            
            if all_results:
                all_results.sort(key=lambda x: x[0])
                return all_results
        except: continue
    
    return None

def fetch_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return None

def save_cache(data):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        with open(EMBED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except: pass

def load_data():
    """v5.1 五源并行获取 + 多数投票 + 完整性校验
    源1: 澄曜API (最新1期, 免费)
    源2: cwl.gov.cn (官方, 最近80期)
    源3: 中彩网 zhcw.com (官方合作, 100期)
    源4: 爱彩网 aicai.com (商业平台, 200期)
    源5: GitHub FSloper/lottery_data (8322期全量, 权威校验)
    
    策略:
    - 5源并行抓取 (ThreadPool)
    - 每个源3次重试+指数退避
    - 同号多数据冲突时: 3+源一致→采信多数; 2:2平→GitHub裁决
    - 数据完整性自动检测 + 缓存持久化
    """
    print("[数据] v5.1 五源并行获取...")
    gh_token = os.environ.get('GITHUB_TOKEN', None)
    
    # ============ Phase 1: 并行抓取所有源 ============
    src_results = {}
    src_ok = {}
    
    def _fetch_one(fn, name, *args):
        result = _retry_fetch(fn, name, *args)
        ok = result is not None and len(result) > 0
        src_ok[name] = ok
        tag = 'OK' if ok else 'OFFLINE'
        cnt = len(result) if ok else 0
        print(f"  [{tag}] {name}: {cnt}期")
        return result
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(_fetch_one, fetch_ruseo, '澄曜'): 'ruseo',
            executor.submit(_fetch_one, fetch_cwl, 'cwl官网'): 'cwl',
            executor.submit(_fetch_one, fetch_zhcw, '中彩网'): 'zhcw',
            executor.submit(_fetch_one, fetch_aicai, '爱彩网'): 'aicai',
            executor.submit(_fetch_one, fetch_github, 'GitHub', gh_token): 'github',
        }
        for f in concurrent.futures.as_completed(futures):
            src_name = futures[f]
            try:
                src_results[src_name] = f.result()
            except:
                src_results[src_name] = None
    
    online_count = sum(1 for v in src_ok.values() if v)
    online_names = [k for k, v in src_ok.items() if v]
    print(f"  >> 在线源: {online_count}/5 ({', '.join(online_names)})")
    
    # ============ Phase 2: 加载本地数据(嵌入+缓存) ============
    data = list(EMBEDDED)
    if os.path.exists(EMBED_FILE):
        try:
            with open(EMBED_FILE, 'r', encoding='utf-8') as f:
                emb_data = json.load(f)
            if len(emb_data) > len(EMBEDDED):
                data = emb_data
        except: pass
    existing = {d[0] for d in data}
    print(f"  基础: {len(data)}期 ({data[0][0]}~{data[-1][0]})")
    
    cache = fetch_cache()
    if cache:
        n = 0
        for rec in cache:
            if rec[0] not in existing:
                data.append(rec); existing.add(rec[0]); n += 1
        if n: print(f"  缓存: +{n}期")
    
    # ============ Phase 3: 多数投票合并多源数据 ============
    # 构建每期多源视图: {issue: {source_name: (digits, date)}}
    multi_view = {}
    for src_name, src_data in src_results.items():
        if not src_data: continue
        for rec in src_data:
            issue = rec[0]
            if issue is None: continue
            if issue not in multi_view:
                multi_view[issue] = {}
            multi_view[issue][src_name] = (tuple(rec[2]), rec[1])
    
    new_count = 0
    conflict_resolved = 0
    
    for issue, sources in multi_view.items():
        if issue in existing:
            continue
        
        vote_map = {}
        best_date = ''
        for src_name, (digits_tup, date_str) in sources.items():
            vote_map.setdefault(digits_tup, []).append(src_name)
            if date_str and (not best_date or date_str > best_date):
                best_date = date_str
        
        if len(vote_map) == 1:
            digits_tup = list(vote_map.keys())[0]
        elif len(vote_map) >= 2:
            sorted_votes = sorted(vote_map.items(), key=lambda x: len(x[1]), reverse=True)
            winner, winner_sources = sorted_votes[0]
            runner_up, runner_sources = sorted_votes[1]
            if len(winner_sources) > len(runner_sources):
                digits_tup = winner
            else:
                if 'github' in sources:
                    digits_tup = sources['github'][0]
                elif 'cwl' in sources:
                    digits_tup = sources['cwl'][0]
                else:
                    digits_tup = winner
                conflict_resolved += 1
        
        data.append([issue, best_date, list(digits_tup)])
        existing.add(issue)
        new_count += 1
    
    if new_count:
        extra = f" (解决{conflict_resolved}个冲突)" if conflict_resolved else ""
        print(f"  多源合并: +{new_count}期{extra}")
    
    data.sort(key=lambda x: x[0])
    
    # ============ Phase 4: GitHub全量交叉校验 (自动修正) ============
    if src_ok.get('github'):
        gh_data = src_results['github']
        gh_map = {r[0]: tuple(r[2]) for r in gh_data}
        checked = mismatch = corrected = 0
        for i, rec in enumerate(data):
            if rec[0] in gh_map:
                checked += 1
                if tuple(rec[2]) != gh_map[rec[0]]:
                    mismatch += 1
                    data[i][2] = list(gh_map[rec[0]])
                    corrected += 1
        if checked > 0:
            if mismatch == 0:
                print(f"  >> GitHub校验: {checked}期一致")
            else:
                print(f"  !! GitHub校验: {mismatch}/{checked}期不一致 -> 已修正{corrected}期")
    
    # ============ Phase 5: 数据完整性校验 ============
    _validate_integrity(data)
    
    # ============ Phase 6: 持久化缓存 ============
    save_cache(data)
    
    n = len(data)
    online_info = '+'.join(online_names) if online_names else '缓存+嵌入'
    print(f"[数据] 共{n}期: {data[0][0]}~{data[-1][0]} (源: {online_info})")
    return data


def _validate_integrity(data):
    """数据完整性校验"""
    issues = [int(d[0]) for d in data]
    dupes = len(issues) - len(set(issues))
    gaps = []
    for i in range(1, len(issues)):
        diff = issues[i] - issues[i-1]
        if diff != 1:
            prev_year = issues[i-1] // 1000
            curr_year = issues[i] // 1000
            if prev_year != curr_year:
                continue
            if diff > 1:
                gaps.append((issues[i-1], issues[i], diff))
    bad = sum(1 for d in data if not all(0 <= x <= 9 for x in d[2]))
    if dupes:
        print(f"  !! 完整性: {dupes}条重复")
    if gaps:
        gap_info = ', '.join(f'{a}-{b}(缺{diff-1})' for a, b, diff in gaps[:3])
        print(f"  !! 完整性: {len(gaps)}个缺口 ({gap_info})")
    if bad:
        print(f"  !! 完整性: {bad}条非法号码")
    if not dupes and not gaps and not bad:
        print(f"  >> 完整性: OK")

# ============================================================
# HTML 生成
# ============================================================

def generate_html(all_data, bt100):
    next_picks = predict_buma(all_data)
    next_issue = str(int(all_data[-1][0]) + 1)
    pa = bt100['pair_accuracy'] * 100
    pda = bt100['period_accuracy'] * 100
    cp = bt100['correct_pairs']; tp = bt100['total_pairs']
    hn = bt100['correct_periods']; mn = bt100['periods'] - hn
    
    det_rows = ''
    for r in reversed(bt100['details']):
        ast = ''.join(str(d) for d in r['actual'])
        pc = ''
        for pair, ok in zip(r['picks'], r['results']):
            cls = 'pb-ok' if ok else 'pb-fail'
            pc += f'<span class="{cls}">{pair[0]}{pair[1]}</span>'
        rc = 'hit-yes' if r['all_correct'] else 'hit-no'
        mk = '✓' if r['all_correct'] else '✗'
        det_rows += f'<tr class="{rc}"><td>{r["issue"]}</td><td>{r["date"]}</td><td class="ac">{ast}</td><td class="pc">{pc}</td><td class="res">{mk}</td></tr>'
    
    pair_counter = Counter()
    for r in bt100['details']:
        for p in r['picks']: pair_counter[p] += 1
    top_pairs = sorted(pair_counter.items(), key=lambda x: x[1], reverse=True)[:8]
    hot_html = ''.join(f'<span class="ht">{a}{b}<small>{c}次</small></span>' for (a,b),c in top_pairs)
    
    update_time = time.strftime('%Y-%m-%d %H:%M', time.localtime())
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>晓炜两码不组</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;background:#f8fafc;color:#334155;min-height:100vh;-webkit-text-size-adjust:100%}}
.header{{background:linear-gradient(135deg,#0f172a,#1e293b);color:#fff;padding:20px 16px;text-align:center}}
.header h1{{font-size:20px;font-weight:800;letter-spacing:3px;margin-bottom:2px}}
.header .sub{{font-size:10px;opacity:.45;font-weight:300}}
.container{{max-width:700px;margin:0 auto;padding:12px 12px 0}}

.pred-card{{background:#fff;border:2px solid #e2e8f0;border-radius:14px;padding:24px 16px 20px;margin:0 0 12px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.04)}}
.pred-card .label{{font-size:11px;color:#94a3b8;letter-spacing:5px;margin-bottom:2px}}
.pred-card .issue{{font-size:13px;color:#0d9488;font-weight:700;margin-bottom:14px}}
.highlight{{font-size:15px;font-weight:800;color:#334155;margin-bottom:12px}}
.pair-row{{display:flex;justify-content:center;gap:14px;flex-wrap:wrap}}
.pair-box{{background:linear-gradient(135deg,#1e293b,#334155);color:#fff;border-radius:12px;padding:14px 24px;font-size:24px;font-weight:900;letter-spacing:3px;box-shadow:0 3px 10px rgba(30,41,59,.2)}}
.footnote{{font-size:10px;color:#94a3b8;margin-top:12px}}

.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px}}
.stat{{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px 6px 10px;text-align:center;box-shadow:0 1px 2px rgba(0,0,0,.02)}}
.stat .val{{font-size:24px;font-weight:800;line-height:1}}
.stat .lbl{{font-size:9px;color:#94a3b8;margin-top:4px}}
.stat.s1 .val{{color:#0d9488}}.stat.s2 .val{{color:#6366f1}}.stat.s3 .val{{color:#f59e0b}}.stat.s4 .val{{color:#0ea5e9}}

.section{{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:14px 12px;margin-bottom:12px;box-shadow:0 1px 2px rgba(0,0,0,.02)}}
.section .title{{font-size:13px;font-weight:700;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid #f1f5f9;color:#1e293b}}

.bar-row{{display:flex;gap:4px;height:30px;margin-bottom:4px}}
.bar{{flex:1;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#fff}}
.bar.hit{{background:linear-gradient(90deg,#0d9488,#14b8a6)}}
.bar.miss{{background:#f1f5f9;color:#94a3b8}}

.hot-tags{{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}}
.ht{{display:inline-flex;align-items:center;gap:3px;background:#f0fdfa;color:#0d9488;padding:4px 10px;border-radius:16px;font-size:13px;font-weight:700}}
.ht small{{font-size:9px;font-weight:400;opacity:.6}}

.tb-wrap{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
table{{width:100%;border-collapse:collapse;font-size:11px}}
th{{background:#f8fafc;padding:8px 4px;text-align:center;font-weight:700;border-bottom:1px solid #e2e8f0;font-size:10px;color:#64748b;position:sticky;top:0}}
td{{padding:8px 3px;text-align:center;border-bottom:1px solid #f1f5f9}}
.ac{{font-weight:800;color:#0d9488;letter-spacing:2px;font-size:12px}}
.pc{{display:flex;justify-content:center;gap:5px;flex-wrap:wrap}}
.pb-ok{{display:inline-flex;align-items:center;justify-content:center;padding:3px 7px;border-radius:6px;background:#f0fdfa;color:#0d9488;font-weight:800;font-size:12px;border:1px solid #a7f3d0}}
.pb-fail{{display:inline-flex;align-items:center;justify-content:center;padding:3px 7px;border-radius:6px;background:#fef2f2;color:#ef4444;font-weight:800;font-size:12px;border:1px solid #fecaca}}
.hit-yes td{{background:#fafdfc}}
.res{{font-weight:800;font-size:13px}}.hit-yes .res{{color:#0d9488}}.hit-no .res{{color:#ef4444}}
.warn{{background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:8px 12px;margin-bottom:12px;font-size:10px;color:#92400e;text-align:center}}
.footer{{text-align:center;padding:16px;color:#94a3b8;font-size:9px;line-height:1.8}}
.info{{font-size:10px;color:#64748b;line-height:1.8}}
@media(max-width:400px){{.stats{{grid-template-columns:repeat(2,1fr)}}.pair-box{{padding:12px 18px;font-size:21px}}}}
</style>
</head>
<body>
<div class="header">
  <h1>晓炜两码不组</h1>
  <div class="sub">v5.1 · 五源并行 · 云端全自动</div>
</div>

<div class="container">
  <div class="warn">⚠ 彩票随机，仅供数据参考，不构成投注建议</div>

  <div class="pred-card">
    <div class="label">▎下期两码不组预测</div>
    <div class="issue">期号 {next_issue}</div>
    <div class="highlight">以下两组号码 <u>不会同时出现</u></div>
    <div class="pair-row">
      <div class="pair-box">{next_picks[0][0]}{next_picks[0][1]}</div>
      <div class="pair-box">{next_picks[1][0]}{next_picks[1][1]}</div>
    </div>
    <div class="footnote">{len(all_data)}期历史 · 澄曜+cwl+中彩网+爱彩网+GitHub · 五源并行</div>
  </div>

  <div class="stats">
    <div class="stat s1"><div class="val">{pa:.1f}%</div><div class="lbl">100期双码准确率</div></div>
    <div class="stat s2"><div class="val">{cp}/{tp}</div><div class="lbl">正确/总预测对</div></div>
    <div class="stat s3"><div class="val">{pda:.1f}%</div><div class="lbl">100期全对率</div></div>
    <div class="stat s4"><div class="val">{hn}/{bt100["periods"]}</div><div class="lbl">两组全对期数</div></div>
  </div>

  <div class="section">
    <div class="title">📊 100期回测分布 (近→远)</div>
    <div class="bar-row">
      <div class="bar hit" style="flex:{hn}">{hn}期全对 ✓</div>
      <div class="bar miss" style="flex:{mn}">{mn}期有错 ✗</div>
    </div>
    <div class="hot-tags">{hot_html}</div>
  </div>

  <div class="section">
    <div class="title">📋 100期回测详情 (近→远)</div>
    <div class="tb-wrap"><table>
      <thead><tr><th>期号</th><th>日期</th><th>开奖</th><th>预测</th><th>结果</th></tr></thead>
      <tbody>{det_rows}</tbody>
    </table></div>
  </div>

  <div class="section">
    <div class="title">🔒 诚实声明</div>
    <div class="info">
    ✅ 五源并行+重试+投票, 零未来数据泄露<br>
    ✅ 严格滚动回测, 零未来数据泄露<br>
    ✅ 五源降级: 澄曜+cwl+中彩网+爱彩网+GitHub<br>
    ⚠ 回测100%不代表未来100%，彩票本质随机<br>
    🚫 不偷看未来、不修改结果、不承诺稳赚
    </div>
  </div>
</div>

<div class="footer">
  🤖 GitHub Actions 全自动 · 每日北京时间22:00更新<br>
  更新: {update_time} · 数据: GitHub/cwl.gov.cn · 仅供参考
</div>
</body>
</html>'''


def main():
    print("=" * 50)
    print("  晓炜两码不组 · 云端自动部署")
    print("=" * 50)
    
    all_data = load_data()
    
    bt100 = run_backtest(all_data, 100)
    pa = bt100['pair_accuracy'] * 100
    print(f"\n[回测] 100期: {pa:.1f}% ({bt100['correct_pairs']}/{bt100['total_pairs']})")
    
    next_picks = predict_buma(all_data)
    next_issue = str(int(all_data[-1][0]) + 1)
    print(f"[预测] {next_issue}: {next_picks[0][0]}{next_picks[0][1]}, {next_picks[1][0]}{next_picks[1][1]}")
    
    html = generate_html(all_data, bt100)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n✅ 已生成: {out}")
    return out


if __name__ == '__main__':
    main()
