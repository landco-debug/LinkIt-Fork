package tech.kalkikgp.linkit

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.widget.Toast

/**
 * Android's native selection-toolbar action, labelled "Linkit".
 *
 * Receive EXTRA_PROCESS_TEXT directly from the app where the user selected
 * the text. Never touch Android's clipboard or modify the originating text.
 * Enqueue the existing signed clipboard handoff and finish immediately;
 * AppTheme.Invisible is a windowNoDisplay theme.
 */
class TextSelectionActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            if (intent?.action != Intent.ACTION_PROCESS_TEXT) return

            val selectedText = intent.getCharSequenceExtra(Intent.EXTRA_PROCESS_TEXT)
                ?.toString()
            if (selectedText.isNullOrBlank()) {
                Toast.makeText(this, "No text selected", Toast.LENGTH_SHORT).show()
                return
            }

            if (IdentityStore(applicationContext).trustedMac() == null) {
                Toast.makeText(this, "Pair Linkit with your Mac first", Toast.LENGTH_LONG).show()
                return
            }

            // Uses the existing Mac endpoint that sets the macOS pasteboard.
            // No Android clipboard read/write, UI launch or browser handoff.
            LinkitSendService.enqueueText(this, "clipboard", selectedText)
            Toast.makeText(this, "Sending to Mac", Toast.LENGTH_SHORT).show()
        } catch (error: Exception) {
            Toast.makeText(
                this,
                "Could not send to Mac: ${error.message ?: "unknown error"}",
                Toast.LENGTH_LONG
            ).show()
        } finally {
            // Mandatory for a windowNoDisplay activity: finish before onResume.
            finish()
        }
    }
}
