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

<script setup lang="ts">
import Rating from '@/types/Rating.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {DeliverableProps} from '@/components/views/order/mixins/DeliverableMixin.ts'
import {useSingle} from '@/store/singles/hooks.ts'

const props = defineProps<Omit<DeliverableProps, "baseName"> & {end: 'buyer' | 'seller'}>()

const rating = useSingle<Rating>(
    `${props.orderId}__rate__${props.end}`,
    {endpoint: `/api/sales/order/${props.orderId}/deliverables/${props.deliverableId}/rate/${props.end}/`},
)
rating.get()
</script>
