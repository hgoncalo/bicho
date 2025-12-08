import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ToastProvider, ToastRenderer } from "@/components/Toast"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "BICHO",
  description: "Football made easy",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ToastProvider>
          {children}
          <ToastRenderer />
        </ToastProvider>
      </body>
    </html>
  );
}
