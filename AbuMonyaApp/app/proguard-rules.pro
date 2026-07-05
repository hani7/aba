# Add project specific ProGuard rules here.
# By default, the flags in this file are applied to all build variants.

# Keep WebView JavaScript interface methods
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# Keep the WebViewClient subclass
-keep class com.abumonyaagency.app.** { *; }

# Suppress warnings about missing classes
-dontwarn okhttp3.**
-dontwarn okio.**
