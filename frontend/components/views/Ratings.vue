<template>
  <ac-load-section :controller="ratings">
    <v-container>
      <ac-profile-header :username="username"></ac-profile-header>
      <ac-paginated :list="ratings">
        <template v-slot:default>
          <v-row no-gutters  >
            <v-col v-for="rating in ratings.list" :key="rating.x.id" class="pb-2" cols="12">
              <v-card>
                <v-card-text>
                  <v-row no-gutters  >
                    <v-col class="text-center text-sm-left" cols="12" sm="2" md="1" >
                      <ac-avatar :user="rating.x.rater"></ac-avatar>
                    </v-col>
                    <v-col class="text-center text-sm-left" cols="12" sm="4" md="2" >
                      <v-rating :readonly="true" dense :value="rating.x.stars"></v-rating>
                    </v-col>
                    <v-col class="text-center text-sm-left" cols="12" sm="6" md="9" v-if="rating.x.comments">
                      <ac-rendered :value="rating.x.comments" />
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

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {ListController} from '@/store/lists/controller'
import Subjective from '@/mixins/subjective'
import Rating from '@/types/Rating'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcAvatar from '@/components/AcAvatar.vue'
import AcRendered from '@/components/wrappers/AcRendered'
import AcProfileHeader from '@/components/views/profile/AcProfileHeader.vue'
import {flatten} from '@/lib/lib'
  @Component({
    components: {AcProfileHeader, AcRendered, AcAvatar, AcPaginated, AcLoadSection},
  })
export default class Ratings extends mixins(Subjective) {
    public ratings: ListController<Rating> = null as unknown as ListController<Rating>

    public created() {
      this.ratings = this.$getList(
        `ratings__${flatten(this.username)}`, {endpoint: `/api/sales/account/${this.username}/ratings/`},
      )
      this.ratings.firstRun()
    }
}
</script>
