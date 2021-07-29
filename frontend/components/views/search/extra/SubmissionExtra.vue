<template>
  <v-row no-gutters>
    <v-col cols="12" class="text-center">
      <v-expansion-panels v-model="panel">
        <v-expansion-panel>
          <v-expansion-panel-header class="pa-1">
            <v-row no-gutters>
              <v-col class="text-center extra-height">
                <v-icon left>settings</v-icon>Search Options
                <v-chip v-if="searchForm.fields.watch_list.value" color="primary" class="mx-1">watchlist</v-chip>
                <v-chip v-if="searchForm.fields.commissions.value" color="secondary" class="mx-1">commissions</v-chip>
                <v-chip v-if="searchForm.fields.minimum_content_rating.value" color="white" light class="mx-1">Content
                  <template v-for="value in contentRatings">
                    <span class="px-1" :key="`rating-${value}-spacer`" />
                    <v-badge dot :key="`rating-${value}`" :color="ratingColor[value]" />
                  </template>
                </v-chip>
              </v-col>
            </v-row>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
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
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-col>
    <v-col v-if="maxSelected > rating" class="py-2">
      <v-alert type="warning">
        Some results may be hidden because your content rating settings are too low.
        <router-link :to="settingsPage">Adjust your content rating settings.</router-link>
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
import Component, {mixins} from 'vue-class-component'
import SearchHints from '../mixins/SearchHints'
import AcBoundField from '@/components/fields/AcBoundField'
import Viewer from '@/mixins/viewer'
import SearchContentRatingMixin from '@/components/views/search/mixins/SearchContentRatingMixin'
  @Component({
    components: {AcBoundField},
  })
export default class SubmissionExtra extends mixins(SearchHints, SearchContentRatingMixin, Viewer) {
    public panel: null|number = null
}
</script>
