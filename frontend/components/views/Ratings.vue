<template>
  <ac-load-section :controller="ratings">
    <v-container>
      <ac-profile-header :username="username" />
      <ac-paginated :list="ratings">
        <template #default>
          <v-row no-gutters>
            <v-col
              v-for="rating in ratings.list"
              :key="rating.x!.id"
              class="pb-2"
              cols="12"
            >
              <v-card>
                <v-card-text>
                  <v-row no-gutters>
                    <v-col
                      class="text-center text-sm-left"
                      cols="12"
                      sm="2"
                      md="1"
                    >
                      <ac-avatar :user="rating.x!.rater" />
                    </v-col>
                    <v-col
                      class="text-center text-sm-left"
                      cols="12"
                      sm="4"
                      md="2"
                    >
                      <v-rating
                        :readonly="true"
                        density="compact"
                        :model-value="starRound(rating.x!.stars)"
                      />
                    </v-col>
                    <v-col
                      v-if="rating.x!.comments"
                      class="text-center text-sm-left"
                      cols="12"
                      sm="6"
                      md="9"
                    >
                      <ac-rendered :value="rating.x!.comments" />
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </ac-paginated>
    </v-container>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcPaginated from "@/components/wrappers/AcPaginated.vue"
import AcAvatar from "@/components/AcAvatar.vue"
import AcRendered from "@/components/wrappers/AcRendered.ts"
import AcProfileHeader from "@/components/views/profile/AcProfileHeader.vue"
import { flatten, starRound } from "@/lib/lib.ts"
import { useList } from "@/store/lists/hooks.ts"
import type { Rating, SubjectiveProps } from "@/types/main"

const props = defineProps<SubjectiveProps>()
const ratings = useList<Rating>(`ratings__${flatten(props.username)}`, {
  endpoint: `/api/sales/account/${props.username}/ratings/`,
})
ratings.firstRun()
</script>
