import dns.resolver, smtplib

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
    server.mail(email)
    code, message = server.rcpt(email)
    server.quit()

    return code == 250
