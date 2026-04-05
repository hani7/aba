import './globals.css';

export const metadata = {
  title: 'SkyBook — حجز رحلات الطيران',
  description: 'احجز رحلاتك بأفضل الأسعار مع SkyBook، بدعم من Duffel.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="ar" dir="rtl">
      <head>
        <link rel="icon" type="image/jpeg" href="/favicon.jpg" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
