CREATE TABLE `voice_account_links` (
	`customer_id` text PRIMARY KEY NOT NULL,
	`legacy_owner` text NOT NULL,
	`linked_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `voice_account_links_legacy_owner_unique` ON `voice_account_links` (`legacy_owner`);