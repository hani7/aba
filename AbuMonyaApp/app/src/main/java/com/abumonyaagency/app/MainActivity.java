package com.abumonyaagency.app;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;
import android.widget.RelativeLayout;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

public class MainActivity extends AppCompatActivity {

    private static final String WEBSITE_URL = "https://abumonyaagency.com";

    private WebView          webView;
    private ProgressBar      progressBar;
    private SwipeRefreshLayout swipeRefresh;
    private RelativeLayout   errorLayout;
    private TextView         errorMessage;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView       = findViewById(R.id.webView);
        progressBar   = findViewById(R.id.progressBar);
        swipeRefresh  = findViewById(R.id.swipeRefresh);
        errorLayout   = findViewById(R.id.errorLayout);
        errorMessage  = findViewById(R.id.errorMessage);

        setupWebView();
        setupSwipeRefresh();

        webView.loadUrl(WEBSITE_URL);
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void setupWebView() {
        WebSettings settings = webView.getSettings();

        // Enable JavaScript (required for modern websites)
        settings.setJavaScriptEnabled(true);

        // DOM storage for localStorage / sessionStorage
        settings.setDomStorageEnabled(true);

        // Allow mixed content (http inside https)
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);

        // Responsive zoom
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);

        // Caching
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        // Media
        settings.setMediaPlaybackRequiresUserGesture(false);

        // User agent — pretend to be Chrome on Android
        settings.setUserAgentString(
            "Mozilla/5.0 (Linux; Android 12; Mobile) AppleWebKit/537.36 " +
            "(KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
        );

        // --- WebViewClient -------------------------------------------
        webView.setWebViewClient(new WebViewClient() {

            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
                progressBar.setVisibility(View.VISIBLE);
                errorLayout.setVisibility(View.GONE);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request,
                                        WebResourceError error) {
                super.onReceivedError(view, request, error);
                if (request.isForMainFrame()) {
                    progressBar.setVisibility(View.GONE);
                    swipeRefresh.setRefreshing(false);
                    errorLayout.setVisibility(View.VISIBLE);
                    errorMessage.setText("تعذّر الاتصال بالإنترنت.\nالرجاء التحقق من اتصالك وإعادة المحاولة.");
                }
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                // Open external links (tel:, mailto:, WhatsApp, etc.) in system apps
                if (!url.startsWith("http://") && !url.startsWith("https://")) {
                    try {
                        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                        startActivity(intent);
                    } catch (Exception ignored) {}
                    return true;
                }
                // Keep same-domain URLs in the WebView
                if (url.contains("abumonyaagency.com")) {
                    return false;
                }
                // Open external URLs in system browser
                Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                startActivity(intent);
                return true;
            }
        });

        // --- WebChromeClient (progress bar) --------------------------
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                super.onProgressChanged(view, newProgress);
                progressBar.setProgress(newProgress);
            }
        });
    }

    private void setupSwipeRefresh() {
        swipeRefresh.setColorSchemeColors(
            getResources().getColor(R.color.gold, getTheme()),
            getResources().getColor(R.color.navy, getTheme())
        );
        swipeRefresh.setOnRefreshListener(() -> {
            errorLayout.setVisibility(View.GONE);
            webView.reload();
        });
    }

    /** Retry button click handler (referenced in XML) */
    public void retryConnection(View view) {
        errorLayout.setVisibility(View.GONE);
        webView.reload();
    }

    // Handle back button — navigate WebView history
    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    // Pause/resume WebView with Activity lifecycle
    @Override
    protected void onPause() {
        super.onPause();
        webView.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        webView.onResume();
    }

    @Override
    protected void onDestroy() {
        webView.destroy();
        super.onDestroy();
    }
}
