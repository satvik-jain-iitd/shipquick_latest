// Fixture (story #185): a screen with no hand-drawn UI. detekt and Konsist must pass it.
// Both read text only; this file is never compiled. Konsist refuses an empty list, so it has a class and an object too.
package fixture.good

import androidx.compose.material.icons.Icons
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable

data class Row(val id: String, val title: String)

object Labels {
    const val GO = "Go"
}

@Composable
fun GoodScreen(rows: List<Row>, onGo: () -> Unit) {
    Text(text = rows.first().title, color = MaterialTheme.colorScheme.primary)
    Button(onClick = onGo) { Text(Labels.GO) }
}
