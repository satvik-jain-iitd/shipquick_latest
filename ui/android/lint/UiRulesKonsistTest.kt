// ShipQuick Android UI lint, the Konsist part (story #185, rule 38). A child copies this file into its test source set.
// It reads source text only; nothing is compiled or run from the app. Pinned: Konsist 0.17.3, JUnit 5.
// Each test name is a rule name. CI reads the JUnit report and checks that the bad fixture fails each one by name.
// The scope is set by -Dshipquick.ui.dir=<path from the repository root>. A child's default is app/src/main.
// The files in a theme folder may name a colour. Konsist refuses an empty list, so the scope needs a file, a class and an object.
import com.lemonappdev.konsist.api.Konsist
import com.lemonappdev.konsist.api.verify.assertFalse
import org.junit.jupiter.api.Test

class UiRulesKonsistTest {
    private val scope = Konsist.scopeFromDirectory(System.getProperty("shipquick.ui.dir") ?: "app/src/main")

    private fun inTheme(path: String) = "/theme/" in path || path.endsWith("/Theme.kt") || path.endsWith("/Color.kt")
    // Every Kotlin file, not only composables: a Modifier extension or a top-level val can draw by hand too.
    private fun filesHave(rx: String) = scope.files.assertFalse { Regex(rx).containsMatchIn(it.text) }

    @Test
    fun no_canvas() = filesHave("""\bCanvas\s*\(""")

    @Test
    fun no_draw_modifiers() = filesHave("""\b(drawBehind|drawWithContent|drawWithCache)\b""")

    @Test
    fun no_raw_color() = scope.files.assertFalse {
        !inTheme(it.path) && Regex("""\bColor\s*\(|\bColor\.[A-Z]""").containsMatchIn(it.text)
    }

    @Test
    fun no_gesture_input() = filesHave("""\b(pointerInput|detectTapGestures|detectDragGestures|draggable|transformable)\b""")

    // A layout or primitive with Modifier.clickable is a fake button. ListItem's own clickable is the M3 way and stays allowed.
    // Limit: one level of nested parentheses inside the call. A deeper or multi-line call can slip past; the reviewer reads for it.
    @Test
    fun no_fake_button() = filesHave("""\b(Box|Row|Column|Spacer|Text|Icon|Image)\((?:[^()]|\([^()]*\))*?\.(clickable|combinedClickable)\b""")

    @Test
    fun no_android_view() = filesHave("""\bAndroidView\b""")

    @Test
    fun no_hand_made_shape() = filesHave("""\b(GenericShape|RoundedCornerShape)\b""")

    @Test
    fun no_custom_shape_class() = scope.classes().assertFalse { it.hasParentWithName("Shape") }

    @Test
    fun no_custom_shape_object() = scope.objects().assertFalse { it.hasParentWithName("Shape") }
}
