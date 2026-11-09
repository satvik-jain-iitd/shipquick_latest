// ShipQuick Android template: a list (story #134). Only Compose Material 3 parts and the theme (rule 38).
// LazyColumn is a layout container; each row is ListItem. Spacing: 16dp = spacing.md.
package com.shipquick.ui.templates

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

data class ListRow(val id: String, val title: String, val subtitle: String)

/** A screen of rows. One FAB for the one main action; the empty state says what to do next. */
@OptIn(ExperimentalMaterial3Api::class) // TopAppBar is experimental in the stable M3 releases
@Composable
fun ListTemplate(
    title: String,
    rows: List<ListRow>,
    onOpen: (ListRow) -> Unit,
    onAdd: () -> Unit,
    snackbarHostState: SnackbarHostState = remember { SnackbarHostState() },
) {
    Scaffold(
        topBar = { TopAppBar(title = { Text(title) }) },
        snackbarHost = { SnackbarHost(snackbarHostState) },
        floatingActionButton = {
            FloatingActionButton(onClick = onAdd) { Icon(Icons.Filled.Add, contentDescription = "Add") }
        },
    ) { padding ->
        if (rows.isEmpty()) {
            Box(Modifier.fillMaxSize().padding(padding).padding(16.dp), contentAlignment = Alignment.Center) {
                Text("Nothing here yet. Tap Add to make the first one.", style = MaterialTheme.typography.bodyLarge)
            }
        } else {
            LazyColumn(Modifier.fillMaxSize().padding(padding)) {
                items(rows, key = { it.id }) { row ->
                    ListItem(
                        headlineContent = { Text(row.title) },
                        supportingContent = { Text(row.subtitle) },
                        modifier = Modifier.clickable { onOpen(row) },
                    )
                    HorizontalDivider()
                }
            }
        }
    }
}
