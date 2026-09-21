CREATE TABLE `voice_recordings` (
	`id` text PRIMARY KEY NOT NULL,
	`owner` text NOT NULL,
	`language` text NOT NULL,
	`text_key` text NOT NULL,
	`transcript` text NOT NULL,
	`object_key` text NOT NULL,
	`mime` text NOT NULL,
	`bytes` integer NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `voice_owner_language` ON `voice_recordings` (`owner`,`language`);