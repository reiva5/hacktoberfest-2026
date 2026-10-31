# Talent Commons

A consolidated talent portal for **companies, talent, projects, funding, and
opportunities**. Browse all listings together, filter by type or location, and
search names, descriptions, tags, and related listing names.

## Run locally

Requires Node.js 20 or newer. No dependencies or build step are needed.

```sh
npm start
```

Open http://127.0.0.1:3000. Set `PORT` to use another port, or `HOST` to change
the listening interface. `npm run check` checks JavaScript syntax.

## Using the portal

- Select **View listing** to read details and explore related listings.
- Select **Add a listing** to share any supported object type.
- Use **Related listing** to connect objects. For example, an opportunity can
  belong to a company, a project, a funding program, or a talent profile.
- Website links accept only HTTP(S) URLs without embedded credentials.
- Initial entries are fictional samples, not live offers or funding programs.

This is a local-first prototype, not a shared publishing service. Additions are
stored in this browser's `localStorage`; other browsers and users cannot see
them. If browser storage is unavailable or full, additions last only for the
current session. Do not enter private or sensitive information. Clearing the
`talent-commons-listings-v1` local storage key restores the samples on reload.

## Extending object types

Add an entry with a unique `id`, a singular `label`, a `plural` label, and an
`icon` to `listingTypes` in `app.js`. The directory filters, creation form,
validation, and relationships use this registry automatically. Optional
`.type-<id>` rules in `styles.css` customize badge colors.

Every listing uses the same schema: `id`, `type`, `title`, `description`,
`location`, `tags`, `url`, and `relatedId`. Relationships reference a listing ID
regardless of its type; connected listings appear in the detail view.

## Verification

There is no automated test framework. Run `npm run check`, then verify search,
each type filter, location filtering, empty results, adding a listing, linked
details, and persistence after reloading in a browser.
