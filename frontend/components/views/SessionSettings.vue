<template>
  <ac-load-section :controller="viewerHandler.user">
    <template #default>
      <v-container fluid>
        <v-card>
          <v-card-text>
            <v-row>
              <v-col v-if="unverifiedInTheocracy" cols="12">
                <v-alert type="error">
                  You are currently accessing Artconomy from a location that has
                  restrictive laws on adult content. You will not be allowed to
                  load adult content unless specific conditions are met.
                  <a
                    href="https://artconomy.com/blog/on-the-recent-anti-porn-laws-and-their-impact-on-artconomy/"
                    >Please read our blog post for more details.</a
                  >
                </v-alert>
              </v-col>
              <v-col v-else cols="12">
                <v-alert
                  type="error"
                  :aria-hidden="patchers.sfw_mode.model ? undefined : true"
                  :class="{ invisible: !patchers.sfw_mode.model }"
                >
                  SFW Mode is enabled. Content settings are disabled while SFW
                  mode is in use.
                </v-alert>
              </v-col>
              <v-col cols="12" md="6" lg="4" order="2" order-md="1">
                <ac-patch-field
                  field-type="ac-birthday-field"
                  label="Birthday"
                  :patcher="patchers.birthday"
                  :disables="unverifiedInTheocracy"
                  :persistent-hint="true"
                  hint="You must be at least 18 years old to view adult content."
                />
              </v-col>
              <v-col
                cols="12"
                md="6"
                lg="8"
                class="text-center mt-5"
                order="1"
                order-md="2"
              >
                <v-btn
                  color="secondary"
                  class="cookie-settings-button"
                  variant="elevated"
                  @click="updateCookieSettings"
                >
                  Update Cookie Settings
                </v-btn>
              </v-col>
              <v-col
                cols="12"
                class="pt-5"
                order="3"
                :class="{ disabled: patchers.sfw_mode.model }"
              >
                <strong
                  >Select the maximum content rating you'd like to see when
                  browsing.</strong
                >
              </v-col>
              <v-col
                cols="12"
                order="4"
                :class="{ disabled: patchers.sfw_mode.model }"
              >
                <ac-patch-field
                  field-type="ac-rating-field"
                  :patcher="patchers.rating"
                  :disabled="!adultAllowed"
                  :show-warning="true"
                  hint="Beep"
                />
              </v-col>
              <v-col cols="12" order="5" />
              <v-col cols="12" sm="6" order="6">
                <ac-patch-field
                  field-type="v-switch"
                  label="SFW Mode"
                  :patcher="patchers.sfw_mode"
                  :instant="true"
                  hint="Overrides your content preferences to only allow clean content. Useful if viewing the site
                      from a work machine."
                  :save-indicator="false"
                  color="primary"
                  persistent-hint
                />
              </v-col>
              <v-col class="pa-2 text-center" cols="12" sm="6" order="7">
                <p class="title">
                  Register, and get access to more cool features like:
                </p>
              </v-col>
              <v-col class="d-flex" cols="12" sm="6" order="8">
                <v-row no-gutters class="justify-content d-flex" align="center">
                  <v-col>
                    <v-img
                      :src="laptop"
                      max-height="30vh"
                      :contain="true"
                      alt="A fox typing away on a laptop."
                    />
                  </v-col>
                </v-row>
              </v-col>
              <v-col class="d-flex" cols="12" sm="6" order="9">
                <v-row no-gutters class="justify-content" align="center">
                  <v-spacer />
                  <v-col>
                    <ul>
                      <li>
                        <strong>Character listings</strong>
                      </li>
                      <li>
                        <strong
                          >Saved Payment information for quick checkout</strong
                        >
                      </li>
                      <li>
                        <strong>Galleries</strong>
                      </li>
                      <li>
                        <strong>Blocked Tags</strong>
                      </li>
                      <li>
                        <strong>...And much more!</strong>
                      </li>
                    </ul>
                  </v-col>
                  <v-spacer />
                </v-row>
              </v-col>
              <v-col class="text-center pt-2" cols="12" order="10">
                <v-btn
                  color="primary"
                  :to="{ name: 'Register' }"
                  variant="flat"
                >
                  Sign up for FREE!
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import { useViewer } from "@/mixins/viewer.ts"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import { differenceInYears } from "date-fns"
import { BASE_URL } from "@/lib/lib.ts"
import { SingleController } from "@/store/singles/controller.ts"
import { parseISO } from "@/lib/otherFormatters.ts"
import { computed, onMounted } from "vue"
import { ArtState } from "@/store/artState.ts"
import { useStore } from "vuex"
import { useRouter } from "vue-router"
import { AnonUser } from "@/store/profiles/types/main"

const { viewerHandler, theocraticBan, isRegistered, rawViewerName } =
  useViewer()
const store = useStore<ArtState>()
const router = useRouter()

const laptop = new URL("/static/images/laptop.png", BASE_URL).href

const patchers = computed(() => {
  return (viewerHandler.user as SingleController<AnonUser>).patchers
})

const unverifiedInTheocracy = computed(() => {
  return theocraticBan.value && !patchers.value.verified_adult.model
})

const updateCookieSettings = () => {
  store.commit("setShowCookieDialog", true)
}

const adultAllowed = computed(() => {
  if (patchers.value.sfw_mode.model) {
    return false
  }
  if (unverifiedInTheocracy.value) {
    return false
  }
  const birthday = patchers.value.birthday.model
  if (birthday === null) {
    return false
  }
  return differenceInYears(new Date(), parseISO(birthday)) >= 18
})

onMounted(() => {
  if (isRegistered.value) {
    router.replace({
      name: "Settings",
      params: { username: rawViewerName.value },
    })
  }
})
</script>

<style scoped>
.disabled {
  opacity: 0.5;
}
.invisible {
  opacity: 0;
}
</style>
