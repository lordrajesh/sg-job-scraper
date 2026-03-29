<?php
/**
 * HK Job Dashboard — Visitor Counter
 * Bot filtering, owner IP exclusion, referrer tracking
 * Deploy to: /hk-jobs/counter.php on Hostinger
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$dir = __DIR__;
$views_file = $dir . '/views.txt';
$visitors_file = $dir . '/visitors.json';
$referrers_file = $dir . '/referrers.json';

// --- Bot Detection ---
function is_bot(): bool {
    $ua = strtolower($_SERVER['HTTP_USER_AGENT'] ?? '');
    $bot_keywords = [
        'bot', 'crawl', 'spider', 'slurp', 'semrush', 'ahrefs', 'mj12bot',
        'dotbot', 'rogerbot', 'facebookexternalhit', 'bingpreview',
        'yandexbot', 'duckduckbot', 'baiduspider', 'sogou', 'exabot',
        'gptbot', 'claudebot', 'chatgpt', 'anthropic',
        'curl', 'wget', 'python-requests', 'httpx', 'go-http',
        'lighthouse', 'pagespeed', 'gtmetrix', 'pingdom', 'uptimerobot',
    ];
    foreach ($bot_keywords as $kw) {
        if (strpos($ua, $kw) !== false) return true;
    }

    // Cloud IP ranges (likely scanners)
    $ip = $_SERVER['REMOTE_ADDR'] ?? '';
    $cloud_prefixes = [
        '20.44.', '20.48.', '20.50.', '20.52.', '20.60.', '20.64.', '20.68.', '20.72.', '20.76.', '20.80.',
        '52.', '54.', '34.', '35.',
    ];
    foreach ($cloud_prefixes as $prefix) {
        if (strpos($ip, $prefix) === 0) return true;
    }

    return false;
}

// --- Owner IP (Telmex IPv6 /64) ---
function is_owner(): bool {
    $ip = $_SERVER['REMOTE_ADDR'] ?? '';
    return strpos($ip, '2806:2a0:1529:87c7') === 0;
}

// --- Referrer Classification ---
function classify_referrer(string $ref): string {
    if (!$ref) return 'direct';
    $host = strtolower(parse_url($ref, PHP_URL_HOST) ?? '');
    if (!$host) return 'direct';

    if (strpos($host, 'google') !== false) return 'google';
    if (strpos($host, 'bing') !== false) return 'bing';
    if (strpos($host, 'yahoo') !== false) return 'yahoo';
    if (strpos($host, 'duckduckgo') !== false) return 'duckduckgo';
    if (strpos($host, 'facebook') !== false || strpos($host, 'fb.') !== false) return 'facebook';
    if (strpos($host, 'linkedin') !== false) return 'linkedin';
    if (strpos($host, 'twitter') !== false || strpos($host, 't.co') !== false) return 'twitter';
    if (strpos($host, 'reddit') !== false) return 'reddit';
    if (strpos($host, 'whatsapp') !== false) return 'whatsapp';
    if (strpos($host, 'climbthesearches') !== false) return 'internal';
    if (strpos($host, 'auramip') !== false) return 'internal';

    return $host;
}

// --- Main ---
$is_bot = is_bot();
$is_owner = is_owner();

// Read current views
$views = file_exists($views_file) ? (int)file_get_contents($views_file) : 0;
$views++;
file_put_contents($views_file, $views);

// Track unique visitors (skip bots and owner)
$unique = 0;
if (!$is_bot && !$is_owner) {
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $visitors = [];
    if (file_exists($visitors_file)) {
        $visitors = json_decode(file_get_contents($visitors_file), true) ?: [];
    }

    $today = date('Y-m-d');
    if (isset($visitors[$ip])) {
        $visitors[$ip]['last_date'] = $today;
        $visitors[$ip]['visits']++;
    } else {
        $visitors[$ip] = [
            'first_date' => $today,
            'last_date' => $today,
            'visits' => 1,
            'user_agent' => substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 200),
        ];
    }

    file_put_contents($visitors_file, json_encode($visitors, JSON_PRETTY_PRINT));
    $unique = count($visitors);

    // Track referrer
    $ref = $_SERVER['HTTP_REFERER'] ?? '';
    $source = classify_referrer($ref);
    $referrers = [];
    if (file_exists($referrers_file)) {
        $referrers = json_decode(file_get_contents($referrers_file), true) ?: [];
    }
    if (!isset($referrers[$today])) $referrers[$today] = [];
    $referrers[$today][$source] = ($referrers[$today][$source] ?? 0) + 1;
    file_put_contents($referrers_file, json_encode($referrers, JSON_PRETTY_PRINT));
}

echo json_encode(['views' => $views, 'unique' => $unique]);
