<template>
  <v-container>
    <ac-paginated :list="promotableUsers" :track-pages="true">
      <template #default>
        <v-container class="pa-0">
          <template
            v-for="(promotable, index) in promotableUsers.list"
            :key="promotable.x!.id"
          >
            <v-card>
              <v-card-text v-if="promotable.x">
                <v-row>
                  <v-col cols="3" class="text-center">
                    <ac-avatar :user="promotable.x.user" />
                  </v-col>
                  <v-col cols="2" class="text-center d-flex justify-center">
                    <div class="align-self-center">
                      Can Promote
                      <ac-indicator :value="promotable.x.allow_promotion" />
                    </div>
                  </v-col>
                  <v-col cols="2" class="text-center d-flex justify-center">
                    <div class="align-self-center">
                      Can Promote Site
                      <ac-indicator
                        :value="promotable.x.allow_site_promotion"
                      />
                    </div>
                  </v-col>
                  <v-col cols="2" class="text-center d-flex justify-center">
                    <div class="align-self-center">
                      Can Promote NSFW
                      <ac-indicator :value="promotable.x.nsfw_promotion" />
                    </div>
                  </v-col>
                  <v-col cols="3" class="text-center d-flex justify-center">
                    <div class="align-self-center">
                      <v-btn
                        color="primary"
                        :to="{
                          name: 'Social',
                          params: { username: promotable.x.user.username },
                        }"
                      >
                        Details
                      </v-btn>
                    </div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
            <v-divider v-if="!(index === promotableUsers.list.length - 1)" />
          </template>
        </v-container>
      </template>
    </ac-paginated>
  </v-container>
</template>

<script setup lang="ts">
import AcPaginated from "@/components/wrappers/AcPaginated.vue"
import { useList } from "@/store/lists/hooks.ts"
import { SocialSettings } from "@/types/main"
import AcAvatar from "@/components/AcAvatar.vue"
import AcIndicator from "@/components/AcIndicator.vue"
import { User } from "@/store/profiles/types/main"

const promotableUsers = useList<SocialSettings & { user: User }>(
  "promotable_users",
  { endpoint: "/api/profiles/resource/promotable/" },
)
promotableUsers.firstRun()
</script>

<style scoped></style>
