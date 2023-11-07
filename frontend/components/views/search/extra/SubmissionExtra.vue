<template>
  <v-row no-gutters>
    <v-col cols="12" class="text-center">
      <v-expansion-panels v-model="panel">
        <v-expansion-panel>
          <v-expansion-panel-title class="pa-1">
            <v-row no-gutters>
              <v-col class="text-center extra-height">
                <v-icon left icon="mdi-cog"/>
                Search Options
                <v-chip v-if="searchForm.fields.watch_list.value" variant="flat" color="primary" class="mx-1">
                  watchlist
                </v-chip>
                <v-chip v-if="searchForm.fields.commissions.value" variant="flat" color="secondary" class="mx-1">
                  commissions
                </v-chip>
                <v-chip v-if="searchForm.fields.minimum_content_rating.value" variant="flat" color="white" light
                        class="mx-1">Content
                  <template v-for="value in contentRatings" :key="`rating-${value}`">
                    <span class="px-1"/>
                    <v-badge dot :color="ratingColor[value]"/>
                  </template>
                </v-chip>
              </v-col>
            </v-row>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-card-text>
              <v-row dense>
                <v-col cols="12" sm="6" md="4" v-if="isRegistered">
                  <ac-bound-field
                      :field="searchForm.fields.watch_list"
                      field-type="ac-checkbox"
                      label="Watch List"
                      :persistent-hint="true"
                      hint="Only return results from artists on my watch list."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                      :field="searchForm.fields.commissions"
                      field-type="ac-checkbox"
                      label="Commissioned Pieces"
                      :persistent-hint="true"
                      hint="Only show submissions commissioned through Artconomy."
                  />
                </v-col>
                <v-col cols="12" sm="12" md="4" v-if="showRatings">
                  <v-select
                      field-type="v-select"
                      label="Content Ratings"
                      :persistent-hint="true"
                      :items="ratingItems"
                      v-model="contentRatings"
                      solo-inverted
                      multiple
                      chips
                      hint="Only show submissions with these ratings."
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-col>
    <v-col v-if="maxSelected > rating" class="py-2">
      <v-alert type="warning">
        Some results may be hidden because your content rating settings are too low.
        <v-btn small @click="ageCheck({value: maxSelected, force: true})" class="rating-button" variant="elevated">Adjust your content
          rating settings.
        </v-btn>
      </v-alert>
    </v-col>
  </v-row>
</template>

<style scoped>
.extra-height {
  line-height: 2.5;
}
</style>

<script lang="ts">
import {Component, mixins, toNative, Watch} from 'vue-facing-decorator'
import SearchHints from '../mixins/SearchHints'
import AcBoundField from '@/components/fields/AcBoundField'
import Viewer from '@/mixins/viewer'
import SearchContentRatingMixin from '@/components/views/search/mixins/SearchContentRatingMixin'

@Component({
  components: {AcBoundField},
})
class SubmissionExtra extends mixins(SearchHints, SearchContentRatingMixin, Viewer) {
  public panel: null | number = null

  @Watch('maxSelected')
  public triggerCheck(value: number) {
    this.ageCheck({value})
  }
}

export default toNative(SubmissionExtra)
</script>
