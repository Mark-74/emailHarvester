import dns.resolver, smtplib, requests, re

PATTERNS = [
    r'^\w{2,}\.\w+$',
    r'^\w\.\w+$',
    r'^\w{2,}$',
]

PROXIES = {
    'http':  'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

def get_mail_from_domain(domain: str) -> list[str]:
    if not domain:
        return []

    results = []
    for i in dns.resolver.resolve(domain, 'MX'):
        results.append(i.exchange.to_text()[:-1])
    
    return results

def verify_email(email: str, smtp: str) -> bool:
    if not email or not smtp:
        return False

    if '@' not in email:
        return False

    server = smtplib.SMTP(smtp)
    server.set_debuglevel(0)

    server.helo()
    server.mail('test@example.it')
    code, _ = server.rcpt(email)
    server.quit()

    return code == 250


def verify_pattern(secure: list[str], predicted: list[str]):
    if not isinstance(secure, list) or not isinstance(predicted, list):
        return

    for email in secure:
        if email in predicted:
            for pattern in PATTERNS:
                if re.match(pattern, email.split('@')[0]):
                    return pattern
                
def test_tor_connection():
    try:
        requests.get('http://httpbin.org/ip', proxies=PROXIES)
    except:
        return False
    return True