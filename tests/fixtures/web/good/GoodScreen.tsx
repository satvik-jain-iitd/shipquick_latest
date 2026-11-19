// Fixture (story #189): a web screen with no hand-drawn UI. The vibe scorer must pass it.
// Read as text only; this file is never compiled, so the component names need not exist.
import { Button, Card, Heading, Stack, Text, TextInput } from '@astryxdesign/core';

export function GoodScreen() {
  return (
    <Card>
      <Stack gap="md">
        <Heading level={1}>Sign in</Heading>
        <TextInput label="Email" type="email" />
        <TextInput label="Password" type="password" />
        <Button variant="primary">Sign in</Button>
        <Text tone="secondary">Forgot password?</Text>
      </Stack>
    </Card>
  );
}
