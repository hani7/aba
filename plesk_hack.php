<?php
/**
 * Diagnostic tool to bypass Plesk permission locks
 */
echo "<h2>Server Diagnostics</h2><pre style='background:#f4f4f4; padding:20px; border-radius:10px;'>";

// 1. Where is Python?
echo "<b>[1] Checking for Python Installation:</b>\n";
if (function_exists('shell_exec')) {
    $out = shell_exec('where python 2>&1');
    if (!$out || trim($out) == "") {
        echo "--> Python path not found! Hosted server might not have it installed natively.\n";
    } else {
        echo trim($out) . "\n";
    }
} else {
    echo "--> Error: Host has disabled the PHP shell_exec function.\n";
}

// 2. What is your exact server path?
echo "\n<b>[2] Checking your Absolute Root Path:</b>\n";
echo __DIR__ . "\n";

echo "</pre>";
?>
