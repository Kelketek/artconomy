<template>
  <v-row no-gutters>
    <v-col cols="12" class="text-center">
      <v-expansion-panels v-model="panel">
        <v-expansion-panel>
          <v-expansion-panel-header class="pa-1">
            <v-row no-gutters>
              <v-col class="text-center extra-height">
                <v-icon left>settings</v-icon>Search Options
                <v-chip v-if="searchForm.fields.shield_only.value" color="green" class="mx-1">shield</v-chip>
                <v-chip v-if="searchForm.fields.watch_list.value" color="primary" class="mx-1">watchlist</v-chip>
                <v-chip v-if="searchForm.fields.featured.value" color="secondary" class="mx-1">featured</v-chip>
                <v-chip v-if="searchForm.fields.rating.value" color="yellow" class="mx-1" light>high rated</v-chip>
                <v-chip v-if="searchForm.fields.max_price.value" color="red" class="mx-1">max price</v-chip>
                <v-chip v-if="searchForm.fields.min_price.value" color="black" class="mx-1">min price</v-chip>
                <v-chip v-if="searchForm.fields.max_turnaround.value" color="teal" class="mx-1">max turnaround</v-chip>
                <v-chip v-if="searchForm.fields.artists_of_color.value" color="orange" class="mx-1" light>Artists of Color</v-chip>
                <v-chip v-if="searchForm.fields.lgbt.value" color="purple" class="mx-1">LGBT+</v-chip>
                <v-chip v-if="searchForm.fields.minimum_content_rating.value" color="white" light class="mx-1">Content
                  <span class="px-1" />
                  <v-badge dot :color="ratingColor[searchForm.fields.minimum_content_rating.value]" />
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
                    :field="searchForm.fields.shield_only"
                    field-type="ac-checkbox"
                    label="Shield Only"
                    :persistent-hint="true"
                    hint="Only show products guaranteed by Artconomy Shield."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                    :field="searchForm.fields.featured"
                    field-type="ac-checkbox"
                    label="Featured"
                    :persistent-hint="true"
                    hint="Only show featured products curated by Artconomy.com's staff."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                    :field="searchForm.fields.rating"
                    field-type="ac-checkbox"
                    label="Best Reviewed First"
                    :persistent-hint="true"
                    hint="Sort from highest reviewed product to lowest."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                    :field="searchForm.fields.artists_of_color"
                    field-type="ac-checkbox"
                    label="Artists of Color"
                    :persistent-hint="true"
                    hint="Find products from Artists of Color."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                    :field="searchForm.fields.lgbt"
                    field-type="ac-checkbox"
                    label="LGBT+"
                    :persistent-hint="true"
                    hint="Find products from LGBTQ+ artists."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                    :field="searchForm.fields.max_price"
                    label="Max Price"
                    :persistent-hint="true"
                    hint="Only show products with a price equal to or lower than this amount."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                    :field="searchForm.fields.min_price"
                    label="Min Price"
                    :persistent-hint="true"
                    hint="Only show products with a price equal to or higher than this amount."
                  />
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <ac-bound-field
                    :field="searchForm.fields.max_turnaround"
                    label="Max Turnaround"
                    :persistent-hint="true"
                    hint="Only show products with an estimated turnaround, in days, at or lower than this."
                  />
                </v-col>
              </v-row>
              <v-row v-if="showRatings">
                <v-col sm="10" md="10" offset-lg="1" offset-sm="1">
                  <ac-bound-field
                      :field="searchForm.fields.minimum_content_rating"
                      field-type="v-select"
                      label="Minimum Content Rating"
                      :persistent-hint="true"
                      :items="ratingItems"
                      outlined
                      hint="Only show products if artists are willing to create content with at least this rating."
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-col>
    <v-col v-if="searchForm.fields.minimum_content_rating.value > rating" class="py-2">
      <v-alert type="warning">
        Some results may be hidden because your content rating settings are too low.
        <v-btn class="rating-button" small @click="ageCheck({value: searchForm.fields.minimum_content_rating.value, force: true})">Adjust your content rating settings.</v-btn>
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
import {Watch} from 'vue-property-decorator'
  @Component({
    components: {AcBoundField},
  })
export default class ProductExtra extends mixins(SearchHints, SearchContentRatingMixin, Viewer) {
    public panel: null|number = null
    @Watch('searchForm.fields.minimum_content_rating.value', {immediate: true})
    public triggerCheck(value: number) {
      if (value) {
        this.ageCheck({value})
      }
    }
}
</script>
