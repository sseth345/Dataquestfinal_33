package com.example.theftdetector.data

import android.content.Context
import android.content.SharedPreferences

class UserPreferences(context: Context) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("user_prefs", Context.MODE_PRIVATE)

    fun setLoggedIn(loggedIn: Boolean) {
        prefs.edit().putBoolean("logged_in", loggedIn).apply()
    }

    fun isLoggedIn(): Boolean {
        return prefs.getBoolean("logged_in", false)
    }

    fun saveUserInfo(email: String, name: String) {
        prefs.edit()
            .putString("email", email)
            .putString("name", name)
            .apply()
    }

    fun getEmail(): String {
        return prefs.getString("email", "") ?: ""
    }

    fun getName(): String {
        return prefs.getString("name", "") ?: ""
    }

    fun clear() {
        prefs.edit().clear().apply()
    }
}
