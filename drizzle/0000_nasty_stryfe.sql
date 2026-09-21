CREATE TABLE `preorders` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`whatsapp` text NOT NULL,
	`created_at` text NOT NULL,
	`consent_version` text NOT NULL,
	`price` integer DEFAULT 39000 NOT NULL,
	`status` text DEFAULT 'registered' NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `preorders_whatsapp_unique` ON `preorders` (`whatsapp`);--> statement-breakpoint
CREATE TABLE `site_settings` (
	`key` text PRIMARY KEY NOT NULL,
	`value` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `submission_limits` (
	`key` text PRIMARY KEY NOT NULL,
	`count` integer NOT NULL,
	`expires` integer NOT NULL
);
