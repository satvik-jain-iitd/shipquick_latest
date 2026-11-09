// ShipQuick Android template: sign-in (story #134). Only Compose Material 3 parts and the theme (rule 38).
// Copy it into the app, rename it, and change the words. Colours and type come from MaterialTheme,
// which the theme built from design/tokens.json fills (story S6). Spacing: 16dp = spacing.md, 24dp = spacing.lg.
package com.shipquick.ui.templates

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.text.input.rememberTextFieldState
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SecureTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp

/** One job: sign in. The filled button is last, at the bottom, and rides on top of the keyboard. */
@Composable
fun SignInTemplate(
    error: String?,
    onSignIn: (email: String, password: String) -> Unit,
    onCreateAccount: () -> Unit,
) {
    val email = rememberTextFieldState()
    val password = rememberTextFieldState()
    Scaffold { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .imePadding()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Text("Sign in", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.padding(top = 24.dp))
            TextField(
                state = email,
                label = { Text("Email") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                modifier = Modifier.fillMaxWidth(),
            )
            SecureTextField(
                state = password,
                label = { Text("Password") },
                isError = error != null,
                supportingText = error?.let { { Text(it) } },
                modifier = Modifier.fillMaxWidth(),
            )
            Spacer(Modifier.weight(1f))
            OutlinedButton(onClick = onCreateAccount, modifier = Modifier.fillMaxWidth()) { Text("Create an account") }
            Button(
                onClick = { onSignIn(email.text.toString(), password.text.toString()) },
                modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp),
            ) { Text("Sign in") }
        }
    }
}
