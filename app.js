// All listing types use the same schema, filters, form, and relationship model.
const listingTypes = [
  { id: "company", label: "Company", plural: "Companies", icon: "▦" },
  { id: "talent", label: "Talent", plural: "Talent", icon: "◎" },
  { id: "project", label: "Project", plural: "Projects", icon: "◇" },
  { id: "funding", label: "Funding", plural: "Funding", icon: "↗" },
  { id: "opportunity", label: "Opportunity", plural: "Opportunities", icon: "✳" },
];

const sampleListings = [
  { id: "company-1", type: "company", title: "Canopy Collective", description: "A small team building thoughtful technology for a greener planet. We connect climate expertise with human-centered design.", location: "London", tags: ["Climate tech", "Design", "Hiring"], relatedId: "", url: "" },
  { id: "talent-1", type: "talent", title: "Alex Morgan", description: "Product designer turning complex problems into accessible experiences. Open to collaborating with purpose-driven teams.", location: "Remote", tags: ["Product design", "Accessibility", "Available"], relatedId: "", url: "" },
  { id: "project-1", type: "project", title: "Open City Atlas", description: "An open-source map of community spaces. Help make local resources easier to discover, one neighborhood at a time.", location: "Global", tags: ["Open source", "Community", "Mapping"], relatedId: "", url: "" },
  { id: "funding-1", type: "funding", title: "The Next Chapter Fund", description: "A sample seed funding program for early-stage ideas with a positive social impact. Supporting the next generation of community builders.", location: "Global", tags: ["Seed funding", "Social impact", "Early stage"], relatedId: "", url: "" },
  { id: "opportunity-1", type: "opportunity", title: "Build for a better climate", description: "A sample collaboration opportunity for developers and designers to explore new climate tools with Canopy Collective.", location: "London", tags: ["Collaboration", "Climate tech"], relatedId: "company-1", url: "" },
  { id: "opportunity-2", type: "opportunity", title: "Help map your neighborhood", description: "Contribute code, research, or local knowledge to Open City Atlas. All experience levels are welcome.", location: "Remote", tags: ["Volunteer", "Open source", "Mapping"], relatedId: "project-1", url: "" },
  { id: "opportunity-3", type: "opportunity", title: "Pitch your community idea", description: "A sample call for community-led projects seeking support from The Next Chapter Fund.", location: "Global", tags: ["Funding call", "Community"], relatedId: "funding-1", url: "" },
];

const storageKey = "talent-commons-listings-v1";
const typeById = new Map(listingTypes.map((type) => [type.id, type]));
const $ = (selector) => document.querySelector(selector);
let activeType = "";

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function safeUrl(value) {
  if (!value) return "";
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) && !url.username && !url.password ? url.href : "";
  } catch {
    return "";
  }
}

function validListing(item) {
  return item && typeof item.id === "string" && item.id.length > 0 && item.id.length <= 100
    && typeById.has(item.type)
    && ["title", "description", "location"].every((key) => typeof item[key] === "string" && item[key].trim().length > 0)
    && item.title.length <= 100 && item.description.length <= 1200 && item.location.length <= 80
    && Array.isArray(item.tags) && item.tags.length <= 6 && item.tags.every((tag) => typeof tag === "string" && tag.length <= 40)
    && typeof item.relatedId === "string" && item.relatedId.length <= 100
    && typeof item.url === "string" && item.url.length <= 500 && (!item.url || safeUrl(item.url));
}

function loadListings() {
  try {
    const saved = localStorage.getItem(storageKey);
    if (saved !== null) {
      const parsed = JSON.parse(saved);
      if (!Array.isArray(parsed) || !parsed.every(validListing) || new Set(parsed.map((item) => item.id)).size !== parsed.length) {
        throw new Error("Invalid saved listings");
      }
      return parsed;
    }
  } catch {
    $("#notice").textContent = "Saved listings could not be loaded. Showing sample listings; new additions may only last for this session.";
  }
  return [...sampleListings];
}

let listings = loadListings();

function badge(typeId) {
  const type = typeById.get(typeId);
  return element("span", `badge type-${type.id}`, `${type.icon} ${type.label}`);
}

function tags(items) {
  const container = element("div", "tags");
  items.forEach((tag) => container.append(element("span", "", tag)));
  return container;
}

function openDetails(listing) {
  const content = $("#detail-content");
  $("#detail-title").textContent = listing.title;
  content.replaceChildren(badge(listing.type), element("p", "location", `◉ ${listing.location}`), element("p", "description", listing.description), tags(listing.tags));
  const related = listings.find((item) => item.id === listing.relatedId);
  if (related) {
    content.append(element("h3", "", "Related listing"), detailButton(related));
  }
  const connected = listings.filter((item) => item.relatedId === listing.id);
  if (connected.length) {
    content.append(element("h3", "", "Connected listings"));
    connected.forEach((item) => content.append(detailButton(item)));
  }
  if (safeUrl(listing.url)) {
    const link = element("a", "button primary external-link", "Visit website ↗");
    link.href = safeUrl(listing.url);
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    content.append(link);
  }
  if (!$("#detail-dialog").open) $("#detail-dialog").showModal();
}

function detailButton(listing) {
  const button = element("button", "text-button", listing.title);
  button.type = "button";
  button.addEventListener("click", () => openDetails(listing));
  return button;
}

function renderListings() {
  const query = $("#search").value.trim().toLocaleLowerCase();
  const location = $("#location").value;
  const matches = listings.filter((listing) => {
    const related = listings.find((item) => item.id === listing.relatedId);
    const searchable = [listing.title, listing.description, listing.location, ...listing.tags, typeById.get(listing.type).label, related?.title || ""].join(" ").toLocaleLowerCase();
    return (!activeType || listing.type === activeType) && (!location || listing.location === location) && searchable.includes(query);
  });
  $("#result-count").textContent = `${matches.length} ${matches.length === 1 ? "listing" : "listings"}${activeType ? ` · ${typeById.get(activeType).plural}` : " across the commons"}`;
  $("#empty-state").hidden = matches.length !== 0;
  $("#listings").replaceChildren();
  matches.forEach((listing) => {
    const card = element("article", "listing-card");
    const top = element("div", "card-top");
    top.append(badge(listing.type), element("span", "card-arrow", "↗"));
    card.append(top, element("h3", "", listing.title), element("p", "location", `◉ ${listing.location}`), element("p", "card-description", listing.description), tags(listing.tags));
    const related = listings.find((item) => item.id === listing.relatedId);
    if (related) card.append(element("p", "related", `Connected to ${related.title}`));
    const button = detailButton(listing);
    button.className = "card-link";
    button.textContent = "View listing →";
    button.setAttribute("aria-label", `View ${listing.title}`);
    card.append(button);
    $("#listings").append(card);
  });
  document.querySelectorAll("[data-type]").forEach((button) => {
    const selected = button.dataset.type === activeType;
    button.setAttribute("aria-pressed", String(selected));
    const count = listings.filter((listing) => !button.dataset.type || listing.type === button.dataset.type).length;
    button.querySelector(".filter-count").textContent = count;
  });
}

function refreshOptions() {
  const selected = $("#location").value;
  $("#location").replaceChildren(new Option("All locations", ""));
  [...new Set(listings.map((listing) => listing.location))].sort().forEach((location) => {
    $("#location").add(new Option(location, location));
  });
  $("#location").value = [...$("#location").options].some((option) => option.value === selected) ? selected : "";
  $("#related-listing").replaceChildren(new Option("No related listing", ""));
  listings.forEach((listing) => $("#related-listing").add(new Option(`${typeById.get(listing.type).label}: ${listing.title}`, listing.id)));
}

[{ id: "", plural: "All listings", icon: "" }, ...listingTypes].forEach((type) => {
  const button = element("button", "filter-button");
  button.type = "button";
  button.dataset.type = type.id;
  button.append(element("span", "", `${type.icon} ${type.plural}`.trim()), element("span", "filter-count"));
  button.addEventListener("click", () => {
    activeType = type.id;
    renderListings();
  });
  $("#type-filters").append(button);
});
listingTypes.forEach((type) => $("#listing-type").add(new Option(type.label, type.id)));

$("#search").addEventListener("input", renderListings);
$("#location").addEventListener("change", renderListings);
$("#clear-filters").addEventListener("click", () => {
  activeType = "";
  $("#search").value = "";
  $("#location").value = "";
  renderListings();
});
$("#add-listing").addEventListener("click", () => {
  $("#listing-form").reset();
  $("#form-error").textContent = "";
  refreshOptions();
  if (activeType) $("#listing-type").value = activeType;
  $("#listing-dialog").showModal();
});
document.querySelectorAll("[data-close]").forEach((button) => {
  button.addEventListener("click", () => document.getElementById(button.dataset.close).close());
});
$("#listing-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const values = new FormData(event.currentTarget);
  const rawUrl = values.get("url").trim();
  const listing = {
    id: crypto.randomUUID(),
    type: values.get("type"),
    title: values.get("title").trim(),
    description: values.get("description").trim(),
    location: values.get("location").trim(),
    tags: [...new Set(values.get("tags").split(",").map((tag) => tag.trim()).filter(Boolean))],
    relatedId: values.get("relatedId"),
    url: rawUrl ? safeUrl(rawUrl) : "",
  };
  if (rawUrl && !listing.url) {
    $("#form-error").textContent = "Use an http:// or https:// website URL without embedded credentials.";
    return;
  }
  if (!validListing(listing) || (listing.relatedId && !listings.some((item) => item.id === listing.relatedId))) {
    $("#form-error").textContent = "Please fill in all required fields and use up to 6 tags of 40 characters each.";
    return;
  }
  listings.unshift(listing);
  try {
    localStorage.setItem(storageKey, JSON.stringify(listings));
    $("#notice").textContent = "Listing added and saved in this browser. It has not been published online.";
  } catch {
    $("#notice").textContent = "Listing added for this session, but browser storage is unavailable. It will be lost when you reload.";
  }
  activeType = "";
  $("#search").value = "";
  $("#location").value = "";
  refreshOptions();
  renderListings();
  $("#listing-dialog").close();
});

refreshOptions();
renderListings();
