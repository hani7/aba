import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="container nav-inner">
        <Link href="/" className="nav-logo">
          <span className="logo-icon">✈</span>
          <span className="logo-text">Sky<span className="gold">Book</span></span>
        </Link>
        <ul className="nav-links">
          <li><Link href="/" className="nav-link">الرئيسية</Link></li>
          <li><Link href="/my-bookings" className="nav-link">حجوزاتي</Link></li>
        </ul>
      </div>
    </nav>
  );
}
