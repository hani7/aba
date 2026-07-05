package com.abumonyaagency.app;

import android.animation.AnimatorSet;
import android.animation.ObjectAnimator;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.view.animation.AccelerateDecelerateInterpolator;
import android.view.animation.DecelerateInterpolator;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

public class SplashActivity extends AppCompatActivity {

    private static final int SPLASH_DURATION = 3000; // 3 seconds

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        // Hide system UI for immersive experience
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        );

        ImageView logoIcon     = findViewById(R.id.splash_logo);
        TextView  titleText    = findViewById(R.id.splash_title);
        TextView  subtitleText = findViewById(R.id.splash_subtitle);
        TextView  taglineText  = findViewById(R.id.splash_tagline);
        View      divider      = findViewById(R.id.splash_divider);

        // --- Logo animation: fade in + scale up -------------------------
        logoIcon.setAlpha(0f);
        logoIcon.setScaleX(0.5f);
        logoIcon.setScaleY(0.5f);

        ObjectAnimator logoAlpha  = ObjectAnimator.ofFloat(logoIcon, "alpha",  0f, 1f);
        ObjectAnimator logoScaleX = ObjectAnimator.ofFloat(logoIcon, "scaleX", 0.5f, 1f);
        ObjectAnimator logoScaleY = ObjectAnimator.ofFloat(logoIcon, "scaleY", 0.5f, 1f);

        AnimatorSet logoSet = new AnimatorSet();
        logoSet.playTogether(logoAlpha, logoScaleX, logoScaleY);
        logoSet.setDuration(700);
        logoSet.setInterpolator(new DecelerateInterpolator());

        // --- Title animation: slide up + fade in ------------------------
        titleText.setAlpha(0f);
        titleText.setTranslationY(40f);

        ObjectAnimator titleAlpha = ObjectAnimator.ofFloat(titleText, "alpha", 0f, 1f);
        ObjectAnimator titleTY    = ObjectAnimator.ofFloat(titleText, "translationY", 40f, 0f);

        AnimatorSet titleSet = new AnimatorSet();
        titleSet.playTogether(titleAlpha, titleTY);
        titleSet.setDuration(600);
        titleSet.setStartDelay(500);
        titleSet.setInterpolator(new DecelerateInterpolator());

        // --- Divider animation ------------------------------------------
        divider.setAlpha(0f);
        divider.setScaleX(0f);
        ObjectAnimator divAlpha  = ObjectAnimator.ofFloat(divider, "alpha", 0f, 1f);
        ObjectAnimator divScaleX = ObjectAnimator.ofFloat(divider, "scaleX", 0f, 1f);
        AnimatorSet divSet = new AnimatorSet();
        divSet.playTogether(divAlpha, divScaleX);
        divSet.setDuration(400);
        divSet.setStartDelay(900);
        divSet.setInterpolator(new AccelerateDecelerateInterpolator());

        // --- Subtitle animation -----------------------------------------
        subtitleText.setAlpha(0f);
        subtitleText.setTranslationY(20f);
        ObjectAnimator subAlpha = ObjectAnimator.ofFloat(subtitleText, "alpha", 0f, 1f);
        ObjectAnimator subTY    = ObjectAnimator.ofFloat(subtitleText, "translationY", 20f, 0f);
        AnimatorSet subSet = new AnimatorSet();
        subSet.playTogether(subAlpha, subTY);
        subSet.setDuration(500);
        subSet.setStartDelay(1100);
        subSet.setInterpolator(new DecelerateInterpolator());

        // --- Tagline animation ------------------------------------------
        taglineText.setAlpha(0f);
        ObjectAnimator tagAlpha = ObjectAnimator.ofFloat(taglineText, "alpha", 0f, 1f);
        tagAlpha.setDuration(600);
        tagAlpha.setStartDelay(1500);

        // Play all animations
        AnimatorSet masterSet = new AnimatorSet();
        masterSet.playTogether(logoSet, titleSet, divSet, subSet, tagAlpha);
        masterSet.start();

        // Navigate to MainActivity after splash duration
        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            Intent intent = new Intent(SplashActivity.this, MainActivity.class);
            startActivity(intent);
            overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
            finish();
        }, SPLASH_DURATION);
    }
}
