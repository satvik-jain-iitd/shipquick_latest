// Template: sign-in. Copy it, then change only the content (rule 38). Standard SwiftUI only.
import SwiftUI

public struct SignInTemplate: View {
    @State private var email = ""
    @State private var password = ""

    public init() {}

    public var body: some View {
        NavigationStack {
            Form {
                Section {
                    TextField("Email", text: $email)
                        .keyboardType(.emailAddress)
                        .textContentType(.username)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    SecureField("Password", text: $password)
                        .textContentType(.password)
                }
                Section {
                    Button("Forgot password?") {}
                }
            }
            .navigationTitle("Sign in")
            .safeAreaInset(edge: .bottom) {
                VStack {
                    Button {} label: { Text("Create account").frame(maxWidth: .infinity) }
                        .buttonStyle(.bordered)
                    Button {} label: { Text("Sign in").frame(maxWidth: .infinity) }
                        .buttonStyle(.borderedProminent)
                        .disabled(email.isEmpty || password.isEmpty)
                }
                .controlSize(.large)
                .padding()
                .background(.bar)
            }
        }
    }
}

#Preview { SignInTemplate() }
