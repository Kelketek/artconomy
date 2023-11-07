<template>
  <ac-load-section :controller="rating">
    <template v-slot:default>
      <v-card v-if="rating.x">
        <v-card-text>
          <v-row no-gutters>
            <v-col class="text-center" cols="12">
              <span class="title">Rate your {{ end }}!</span>
            </v-col>
            <v-col class="text-center" cols="12">
              <ac-patch-field :patcher="rating.patchers.stars" field-type="ac-star-field"></ac-patch-field>
            </v-col>
            <v-col cols="12">
              <ac-patch-field :patcher="rating.patchers.comments" field-type="ac-editor"
                              v-if="rating.x.stars"></ac-patch-field>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import {Component, Prop, toNative} from 'vue-facing-decorator'
import {SingleController} from '@/store/singles/controller'
import Rating from '@/types/Rating'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcProfileHeader from '@/components/views/profile/AcProfileHeader.vue'
import {ArtVue} from '@/lib/lib'

@Component({
  components: {
    AcProfileHeader,
    AcPatchField,
    AcLoadSection,
  },
})
class AcDeliverableRating extends ArtVue {
  @Prop({required: true})
  public orderId!: number

  @Prop({required: true})
  public deliverableId!: number

  @Prop({required: true})
  public end!: 'buyer' | 'seller'

  public rating: SingleController<Rating> = null as unknown as SingleController<Rating>

  public created() {
    this.rating = this.$getSingle(
        `${this.orderId}__rate__${this.end}`,
        {endpoint: `/api/sales/order/${this.orderId}/deliverables/${this.deliverableId}/rate/${this.end}/`},
    )
    this.rating.get()
  }
}

export default toNative(AcDeliverableRating)
</script>
