package com.example.theftdetector

import android.Manifest
import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.core.app.ActivityCompat
import androidx.credentials.CredentialManager
import androidx.credentials.GetCredentialRequest
import androidx.lifecycle.lifecycleScope
import com.example.theftdetector.data.UserPreferences
import com.google.android.libraries.identity.googleid.GetGoogleIdOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import com.google.firebase.FirebaseApp
import com.google.firebase.auth.AuthResult
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.GoogleAuthProvider
import com.google.firebase.auth.OAuthProvider
import com.google.firebase.firestore.FirebaseFirestore
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    private lateinit var auth: FirebaseAuth
    private lateinit var firestore: FirebaseFirestore
    private val credentialManager by lazy { CredentialManager.create(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ✅ Initialize Firebase
        FirebaseApp.initializeApp(this)
        auth = FirebaseAuth.getInstance()
        firestore = FirebaseFirestore.getInstance()

        // ✅ Ask Notification Permission (Android 13+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ActivityCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                requestPermissions(
                    arrayOf(Manifest.permission.POST_NOTIFICATIONS),
                    1
                )
            }
        }

        // ✅ Setup repeating notifications (every 5 minutes)
        setupThreatNotification()

        // ✅ Show splash + navigation
        showSplash()
    }

    private fun setupThreatNotification() {
        val alarmManager = getSystemService(ALARM_SERVICE) as AlarmManager
        val intent = Intent(this, ThreatReceiver::class.java)
        val pendingIntent = PendingIntent.getBroadcast(
            this,
            0,
            intent,
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

        // 🔔 Repeat every 5 minutes
        alarmManager.setRepeating(
            AlarmManager.RTC_WAKEUP,
            System.currentTimeMillis(),
            5 * 1000,
            pendingIntent
        )
    }

    private fun showSplash() {
        setContent {
            AppNavigation(
                onGoogleSignIn = { signInWithGoogle() },
                onGitHubSignIn = { launchGitHubLogin() },
                onLogout = { logoutUser() }
            )
        }
    }

    // ---------------- Google Sign In ----------------
    private fun signInWithGoogle() {
        val option = GetGoogleIdOption.Builder()
            .setFilterByAuthorizedAccounts(false)
            .setServerClientId(getString(R.string.default_web_client_id))
            .build()

        val request = GetCredentialRequest.Builder()
            .addCredentialOption(option)
            .build()

        lifecycleScope.launch {
            try {
                val result = credentialManager.getCredential(this@MainActivity, request)
                val credential = result.credential

                when (credential) {
                    is GoogleIdTokenCredential -> {
                        handleGoogleCred(credential)
                    }
                    is androidx.credentials.CustomCredential -> {
                        if (credential.type ==
                            "com.google.android.libraries.identity.googleid.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL"
                        ) {
                            val googleIdTokenCredential =
                                GoogleIdTokenCredential.createFrom(credential.data)
                            handleGoogleCred(googleIdTokenCredential)
                        } else {
                            Log.e("GoogleSignIn", "Unknown custom credential: ${credential.type}")
                        }
                    }
                    else -> {
                        Log.e("GoogleSignIn", "Unsupported credential type")
                    }
                }
            } catch (e: Exception) {
                Log.e("GoogleSignIn", "Sign-in failed", e)
            }
        }
    }

    private fun handleGoogleCred(credential: GoogleIdTokenCredential) {
        firebaseAuthWithGoogle(credential.idToken)
    }

    private fun firebaseAuthWithGoogle(idToken: String) {
        val creds = GoogleAuthProvider.getCredential(idToken, null)
        auth.signInWithCredential(creds).addOnCompleteListener(this) { task ->
            if (task.isSuccessful) {
                saveUserPrefs()
                reloadHome()
            } else {
                Log.e("GoogleSignIn", "Firebase auth failed", task.exception)
            }
        }
    }

    // ---------------- GitHub Login ----------------
    private fun launchGitHubLogin() {
        val provider = OAuthProvider.newBuilder("github.com")
        val pending = auth.pendingAuthResult
        if (pending != null) {
            pending.addOnSuccessListener { handleGitHubResult(it) }
                .addOnFailureListener { Log.e("GitHubLogin", "error", it) }
        } else {
            auth.startActivityForSignInWithProvider(this, provider.build())
                .addOnSuccessListener { handleGitHubResult(it) }
                .addOnFailureListener { Log.e("GitHubLogin", "error", it) }
        }
    }

    private fun handleGitHubResult(result: AuthResult) {
        saveUserPrefs()
        reloadHome()
    }

    // ---------------- Logout ----------------
    private fun logoutUser() {
        auth.signOut()
        lifecycleScope.launch {
            UserPreferences(this@MainActivity).clear()
        }
        reloadHome()
    }

    private fun saveUserPrefs() {
        val user = auth.currentUser!!
        lifecycleScope.launch {
            UserPreferences(this@MainActivity).apply {
                setLoggedIn(true)
                saveUserInfo(user.email ?: "", user.displayName ?: "")
            }
        }
    }

    private fun reloadHome() {
        setContent {
            AppNavigation(
                onGoogleSignIn = {},
                onGitHubSignIn = {},
                onLogout = { logoutUser() }
            )
        }
    }
}
