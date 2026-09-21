export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
  public: {
    Tables: {
      account_access: {
        Row: {
          account_status: string
          admin_role: boolean
          created_at: string
          updated_at: string
          user_id: string
        }
        Insert: {
          account_status?: string
          admin_role?: boolean
          created_at?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          account_status?: string
          admin_role?: boolean
          created_at?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      activity_progress: {
        Row: {
          activity_id: string
          attempt_count: number
          category_id: string
          child_id: string
          completed_at: string | null
          created_at: string
          duration_seconds: number
          id: string
          is_correct: boolean | null
          updated_at: string
          user_id: string
        }
        Insert: {
          activity_id: string
          attempt_count?: number
          category_id: string
          child_id: string
          completed_at?: string | null
          created_at?: string
          duration_seconds?: number
          id?: string
          is_correct?: boolean | null
          updated_at?: string
          user_id: string
        }
        Update: {
          activity_id?: string
          attempt_count?: number
          category_id?: string
          child_id?: string
          completed_at?: string | null
          created_at?: string
          duration_seconds?: number
          id?: string
          is_correct?: boolean | null
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "activity_progress_child_id_user_id_fkey"
            columns: ["child_id", "user_id"]
            isOneToOne: false
            referencedRelation: "children"
            referencedColumns: ["id", "parent_user_id"]
          },
          {
            foreignKeyName: "activity_progress_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
        ]
      }
      admin_audit_logs: {
        Row: {
          action: string
          admin_user_id: string
          after_data: Json
          before_data: Json
          created_at: string
          id: string
          idempotency_key: string
          target_id: string
          target_type: string
        }
        Insert: {
          action: string
          admin_user_id: string
          after_data?: Json
          before_data?: Json
          created_at?: string
          id?: string
          idempotency_key: string
          target_id: string
          target_type: string
        }
        Update: {
          action?: string
          admin_user_id?: string
          after_data?: Json
          before_data?: Json
          created_at?: string
          id?: string
          idempotency_key?: string
          target_id?: string
          target_type?: string
        }
        Relationships: []
      }
      children: {
        Row: {
          age_band: string
          created_at: string
          display_name: string
          id: string
          parent_user_id: string
          preferred_language: string
          updated_at: string
        }
        Insert: {
          age_band: string
          created_at?: string
          display_name: string
          id?: string
          parent_user_id: string
          preferred_language?: string
          updated_at?: string
        }
        Update: {
          age_band?: string
          created_at?: string
          display_name?: string
          id?: string
          parent_user_id?: string
          preferred_language?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "children_parent_user_id_fkey"
            columns: ["parent_user_id"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
        ]
      }
      marketing_leads: {
        Row: {
          child_age_band: string
          consent_version: string
          created_at: string
          email_normalized: string
          email_verified_at: string | null
          id: string
          landing_page: string | null
          marketing_consent_at: string | null
          parent_name: string
          preferred_language: string
          privacy_consent_at: string
          referral_code: string | null
          status: string
          updated_at: string
          utm_campaign: string | null
          utm_content: string | null
          utm_medium: string | null
          utm_source: string | null
          utm_term: string | null
          whatsapp_e164: string
        }
        Insert: {
          child_age_band: string
          consent_version: string
          created_at?: string
          email_normalized: string
          email_verified_at?: string | null
          id?: string
          landing_page?: string | null
          marketing_consent_at?: string | null
          parent_name: string
          preferred_language?: string
          privacy_consent_at: string
          referral_code?: string | null
          status?: string
          updated_at?: string
          utm_campaign?: string | null
          utm_content?: string | null
          utm_medium?: string | null
          utm_source?: string | null
          utm_term?: string | null
          whatsapp_e164: string
        }
        Update: {
          child_age_band?: string
          consent_version?: string
          created_at?: string
          email_normalized?: string
          email_verified_at?: string | null
          id?: string
          landing_page?: string | null
          marketing_consent_at?: string | null
          parent_name?: string
          preferred_language?: string
          privacy_consent_at?: string
          referral_code?: string | null
          status?: string
          updated_at?: string
          utm_campaign?: string | null
          utm_content?: string | null
          utm_medium?: string | null
          utm_source?: string | null
          utm_term?: string | null
          whatsapp_e164?: string
        }
        Relationships: []
      }
      profiles: {
        Row: {
          created_at: string
          full_name: string
          id: string
          preferred_language: string
          timezone: string
          updated_at: string
          whatsapp_e164: string | null
        }
        Insert: {
          created_at?: string
          full_name: string
          id: string
          preferred_language?: string
          timezone?: string
          updated_at?: string
          whatsapp_e164?: string | null
        }
        Update: {
          created_at?: string
          full_name?: string
          id?: string
          preferred_language?: string
          timezone?: string
          updated_at?: string
          whatsapp_e164?: string | null
        }
        Relationships: []
      }
      subscriptions: {
        Row: {
          access_expires_at: string | null
          access_starts_at: string | null
          activated_by: string | null
          created_at: string
          currency: string
          id: string
          payment_reference: string | null
          plan_code: string
          price_paid: number
          status: string
          updated_at: string
          user_id: string
        }
        Insert: {
          access_expires_at?: string | null
          access_starts_at?: string | null
          activated_by?: string | null
          created_at?: string
          currency?: string
          id?: string
          payment_reference?: string | null
          plan_code?: string
          price_paid?: number
          status?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          access_expires_at?: string | null
          access_starts_at?: string | null
          activated_by?: string | null
          created_at?: string
          currency?: string
          id?: string
          payment_reference?: string | null
          plan_code?: string
          price_paid?: number
          status?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "subscriptions_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "profiles"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      littlefinger_has_access: { Args: never; Returns: boolean }
      littlefinger_schema_version: { Args: never; Returns: number }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends (DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never) = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends (PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never) = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
