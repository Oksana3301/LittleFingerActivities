import {integer,sqliteTable,text,index} from 'drizzle-orm/sqlite-core';
export const preorders=sqliteTable('preorders',{id:text('id').primaryKey(),name:text('name').notNull(),whatsapp:text('whatsapp').notNull().unique(),createdAt:text('created_at').notNull(),consentVersion:text('consent_version').notNull(),price:integer('price').notNull().default(39000),status:text('status').notNull().default('registered')});
export const siteSettings=sqliteTable('site_settings',{key:text('key').primaryKey(),value:text('value').notNull()});
export const submissionLimits=sqliteTable('submission_limits',{key:text('key').primaryKey(),count:integer('count').notNull(),expires:integer('expires').notNull()});

export const voiceRecordings=sqliteTable('voice_recordings',{id:text('id').primaryKey(),owner:text('owner').notNull(),language:text('language').notNull(),textKey:text('text_key').notNull(),transcript:text('transcript').notNull(),objectKey:text('object_key').notNull(),mime:text('mime').notNull(),bytes:integer('bytes').notNull(),updatedAt:text('updated_at').notNull()},table=>[index('voice_owner_language').on(table.owner,table.language)]);
