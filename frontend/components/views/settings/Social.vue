<template>
  <ac-load-section :controller="socialSettings">
    <template #default>
      <v-container fluid class="pa-0">
        <v-card>
          <v-card-text>
            <v-list-subheader class="mb-5">
              <strong>Promotion settings</strong>
            </v-list-subheader>
            <v-row>
              <v-col cols="12">
                <v-alert type="info">
                  We love to promote the artists using our site! These settings
                  give us permission to promote you on social media, or
                  otherwise promote the site using your work, if you choose to
                  allow it.
                  <strong
                    >Since these deal with your rights, they are all opt-in.
                    Opting in helps us all grow!</strong
                  >
                </v-alert>
              </v-col>
              <v-col cols="12" md="6">
                <p>
                  Check this to allow us to promote you and your content on
                  social media. We will link/ping your account on the relevant
                  service (if you've specified it below) when we do this.
                </p>
                <ac-patch-field
                  field-type="ac-checkbox"
                  label="Allow Promotion"
                  :patcher="socialSettings.patchers.allow_promotion"
                />
                <v-divider />
              </v-col>
              <v-col cols="12" md="6">
                <p>
                  Check this to allow us to use your content to promote the site
                  in a general sense-- such as using screenshots containing your
                  content. We may not always ping you in this case, but we may
                  if the content is heavily focused.
                </p>
                <ac-patch-field
                  field-type="ac-checkbox"
                  label="Allow Site Promotion"
                  :patcher="socialSettings.patchers.allow_site_promotion"
                />
                <v-divider />
              </v-col>
              <v-col cols="12" md="6">
                <p>
                  Whether we may promote your NSFW content on social media which
                  allows such content, if applicable.
                </p>
                <ac-patch-field
                  field-type="ac-checkbox"
                  label="NSFW Promotion"
                  :patcher="socialSettings.patchers.nsfw_promotion"
                />
                <v-divider />
              </v-col>
              <v-col cols="12">
                <p>
                  A quick description of your art/style/offerings, for use by
                  our social media specialist when promoting you.
                </p>
                <ac-patch-field
                  field-type="ac-editor"
                  label="Tagline"
                  :patcher="socialSettings.patchers.quick_description"
                />
              </v-col>
              <v-col cols="12">
                <p>Any other information we should know when promoting you.</p>
                <ac-patch-field
                  field-type="ac-editor"
                  label="Promotion Notes"
                  :patcher="socialSettings.patchers.promotion_notes"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <v-card class="mt-3">
          <v-card-text>
            <v-list-subheader class="mb-5">
              <strong>Social Media Links</strong>
            </v-list-subheader>
            <v-row>
              <v-col cols="12">
                <p>
                  Add links to your social media accounts! We'll reference these
                  to ping you when promoting you on social media.
                </p>
              </v-col>
              <v-col cols="12">
                <v-row>
                  <v-col cols="12" md="6" offset-md="3">
                    <ac-load-section :controller="socialLinks">
                      <ac-form-container v-bind="socialLinkForm.bind">
                        <ac-form
                          :form="socialLinkForm"
                          @submit.prevent="
                            socialLinkForm.submitThen(socialLinks.push)
                          "
                        >
                          <ac-bound-field
                            :field="socialLinkForm.fields.url"
                            label="Profile URL"
                            hint="Enter the URL of your social media profile. We'll link it to your account."
                          >
                            <template #append>
                              <v-btn
                                icon
                                color="green"
                                type="submit"
                                aria-label="Submit"
                              >
                                <v-icon>{{ mdiPlus }}</v-icon>
                              </v-btn>
                            </template>
                          </ac-bound-field>
                        </ac-form>
                      </ac-form-container>
                      <v-list>
                        <ac-social-link
                          v-for="link in socialLinks.list"
                          :key="link.x!.id"
                          :link="link"
                          :controls="controls"
                        />
                      </v-list>
                    </ac-load-section>
                  </v-col>
                </v-row>
              </v-col>
              <v-col cols="12" md="6">
                <p>
                  <strong>This feature not yet available.</strong> Check this
                  box to display your links to other sites on your profile.
                  Otherwise these will only be used in connection with
                  promotional work as mentioned above, or with contacting you in
                  an emergency if your main contact isn't working.
                </p>
                <ac-patch-field
                  field-type="ac-checkbox"
                  label="Display Media Links"
                  :patcher="socialSettings.patchers.display_socials"
                />
                <v-divider />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import { SocialLink, SocialSettings, SubjectiveProps } from "@/types/main"
import { useSingle } from "@/store/singles/hooks.ts"
import { useList } from "@/store/lists/hooks.ts"
import { useErrorHandling } from "@/mixins/ErrorHandling.ts"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcSocialLink from "@/components/views/settings/social/AcSocialLink.vue"
import { useSubject } from "@/mixins/subjective.ts"
import AcFormContainer from "@/components/wrappers/AcFormContainer.vue"
import { useForm } from "@/store/forms/hooks.ts"
import AcForm from "@/components/wrappers/AcForm.vue"
import AcBoundField from "@/components/fields/AcBoundField.ts"
import { mdiPlus } from "@mdi/js"

const props = defineProps<SubjectiveProps>()
const { setError } = useErrorHandling()
const { controls } = useSubject({ props })

const socialSettings = useSingle<SocialSettings>(
  `${props.username}__socialPrefs`,
  { endpoint: `/api/profiles/account/${props.username}/social-settings/` },
)
socialSettings.get().catch(setError)
const socialLinks = useList<SocialLink>(`${props.username}__socialLinks`, {
  endpoint: `/api/profiles/account/${props.username}/social-links/`,
  paginated: false,
})
socialLinks.firstRun()
const socialLinkForm = useForm(`${props.username}__newSocialLink`, {
  fields: { url: { value: "" } },
  endpoint: `/api/profiles/account/${props.username}/social-links/from-url/`,
})
</script>

<style scoped></style>
