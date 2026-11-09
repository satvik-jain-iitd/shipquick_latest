// ShipQuick Android template: settings (story #134). Only Compose Material 3 parts and the theme (rule 38).
// Each row takes the tap and the control gets a null click, as Google's accessibility page says
// (developer.android.com/develop/ui/compose/accessibility/api-defaults). Spacing: 16dp = spacing.md.
package com.shipquick.ui.templates

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.toggleable
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp

/** A switch setting, a one-of-many choice, and sign out behind a confirm dialog (a danger pair, never the default). */
@OptIn(ExperimentalMaterial3Api::class) // TopAppBar is experimental in the stable M3 releases
@Composable
fun SettingsTemplate(
    notificationsOn: Boolean,
    onNotificationsChange: (Boolean) -> Unit,
    themes: List<String>,
    theme: String,
    onThemeChange: (String) -> Unit,
    onSignOut: () -> Unit,
) {
    var confirmSignOut by remember { mutableStateOf(false) }
    Scaffold(topBar = { TopAppBar(title = { Text("Settings") }) }) { padding ->
        LazyColumn(Modifier.fillMaxSize().padding(padding)) {
            item {
                ListItem(
                    headlineContent = { Text("Notifications") },
                    supportingContent = { Text("Tell me when something changes") },
                    trailingContent = { Switch(checked = notificationsOn, onCheckedChange = null) },
                    modifier = Modifier.toggleable(value = notificationsOn, role = Role.Switch, onValueChange = onNotificationsChange),
                )
                HorizontalDivider()
                Text("Theme", style = MaterialTheme.typography.titleSmall, modifier = Modifier.padding(16.dp))
            }
            items(themes) { option ->
                ListItem(
                    headlineContent = { Text(option) },
                    leadingContent = { RadioButton(selected = option == theme, onClick = null) },
                    modifier = Modifier.selectable(selected = option == theme, role = Role.RadioButton, onClick = { onThemeChange(option) }),
                )
            }
            item {
                HorizontalDivider()
                ListItem(
                    headlineContent = { Text("Sign out", color = MaterialTheme.colorScheme.error) },
                    modifier = Modifier.clickable(role = Role.Button) { confirmSignOut = true },
                )
            }
        }
    }
    if (confirmSignOut) {
        AlertDialog(
            onDismissRequest = { confirmSignOut = false },
            title = { Text("Sign out?") },
            text = { Text("You will need your password to sign in again.") },
            confirmButton = { TextButton(onClick = { confirmSignOut = false; onSignOut() }) { Text("Sign out") } },
            dismissButton = { TextButton(onClick = { confirmSignOut = false }) { Text("Stay signed in") } },
        )
    }
}
