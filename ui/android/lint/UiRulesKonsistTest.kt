// ShipQuick Android UI lint, the Konsist part (story #185, rule 38). A child copies this file into its test source set.
// It reads source text only; nothing is compiled or run from the app. Pinned: Konsist 0.17.3, JUnit 5.
// Each test name is a rule name. CI reads the JUnit report and checks that the bad fixture fails each one by name.
// The scope is set by -Dshipquick.ui.dir=<path from the project root>. A child's default is its main source folder.
// The files in a theme folder may name a colour. Konsist refuses an empty list, so the scope needs a composable, a class and an object.
import com.lemonappdev.konsist.api.Konsist
import com.lemonappdev.konsist.api.ext.list.withAnnotationNamed
import com.lemonappdev.konsist.api.verify.assertFalse
import org.junit.jupiter.api.Test

class UiRulesKonsistTest {
    private val scope = Konsist.scopeFromDirectory(System.getProperty("shipquick.ui.dir") ?: "src/main")
    private val composables = scope.functions().withAnnotationNamed("Composable")

    private fun inTheme(path: String) = "/theme/" in path || path.endsWith("/Theme.kt") || path.endsWith("/Color.kt")
    private fun composableHas(rx: String) = composables.assertFalse { Regex(rx).containsMatchIn(it.text) }

    @Test
    fun no_canvas() = composableHas("""\bCanvas\s*\(""")

    @Test
    fun no_draw_modifiers() = composableHas("""\b(drawBehind|drawWithContent|drawWithCache)\b""")

    @Test
    fun no_raw_color() = composables.assertFalse {
        !inTheme(it.containingFile.path) && Regex("""\bColor\s*\(|\.background\(\s*Color\.""").containsMatchIn(it.text)
    }

    @Test
    fun no_hand_made_shape() = composableHas("""\b(GenericShape|RoundedCornerShape)\b""")

    @Test
    fun no_custom_shape_class() = scope.classes().assertFalse { it.hasParentWithName("Shape") }

    @Test
    fun no_custom_shape_object() = scope.objects().assertFalse { it.hasParentWithName("Shape") }
}
