# UAT checklist: the dev -> main promotion gate

Put this as a `## UAT on dev (<dev link>)` section in the body of the `dev -> main` release PR. The coder writes it from each story's scenarios; the reviewer checks every line is followable — by a new user who has never seen the app — before asking the owner to test. `scripts/review_merge.sh` refuses the PR while the section is missing, a story line is not followable (`scripts/check_uat.py`), or any box is still unticked.

Every story line needs:
- **Open:** the exact link or screen, with the test data to use (a real phone number, test card, sample file — never "some data").
- Numbered steps, one action each.
- **Expected:** what the tester must see, in plain words, with exact text where there is text.

Plus two fixed checklist lines and one `Known bugs going to production:` line (`none`, or the list).

## Worked example

```
## UAT on dev (https://dev.app.example.com)

- [ ] #219 Fix: cart total after removing an item
  Open: https://dev.app.example.com/cart (log in with test phone 9999999999, OTP 123456)
  1. Add "Masala Dosa" 3 times.
  2. Tap the minus on "Masala Dosa" once.
  Expected: the cart shows 2 x Masala Dosa and the total is ₹240 (2 x ₹120).
- [ ] Old flows still work
- [ ] Design matches the approved boards
Known bugs going to production: none
```

The owner ticks every box on the dev link itself, then approves. An unticked box pulls that story from the release or sends it back to be fixed.
