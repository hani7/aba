import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';

export const metadata = {
  title: 'SkyBook — حجز رحلات الطيران',
  description: 'احجز رحلاتك بأفضل الأسعار مع SkyBook، بدعم من Duffel.',
};

export default function ClientLayout({ children }) {
  return (
    <>
      <Navbar />
      <main>{children}</main>
      <Footer />
    </>
  );
}
